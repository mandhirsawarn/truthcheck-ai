from __future__ import annotations
import mimetypes
import os
from datetime import datetime, timezone
from pathlib import Path
from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.db import get_async_db
from app.exceptions import (
FileTooLargeError,
JobAlreadyCompletedError,
JobNotFoundError,
UnsupportedFormatError,
)
from app.models import Job
from app.schemas import (
ChunkUploadResponse,
JobStage,
UploadCompleteRequest,
UploadCompleteResponse,
UploadInitRequest,
UploadInitResponse,
)
from app.storage import assemble_chunks, cleanup_job, save_chunk, save_single_upload
from app.worker import enqueue_job
router = APIRouter(prefix="/uploads", tags=["uploads"])
CHUNK_SIZE_LIMIT = 10 * 1024 * 1024
def _infer_extension(filename: str, mime_type: str | None = None) -> str:
    _, ext = os.path.splitext(filename)
    if ext:
        return ext.lower()
    if mime_type:
        guessed = mimetypes.guess_extension(mime_type.split(";")[0].strip())
        if guessed:
            return guessed
    return ".mp4"
def _validate_mime(mime_type: str) -> None:
    base = mime_type.split(";")[0].strip().lower()
    if base not in [m.lower() for m in settings.ALLOWED_MIME_TYPES]:
        raise UnsupportedFormatError(
            f"MIME type '{base}' is not supported. "
            f"Allowed: {', '.join(settings.ALLOWED_MIME_TYPES)}",
            detail={"provided_mime": mime_type, "allowed": settings.ALLOWED_MIME_TYPES},
        )
@router.post("/init", response_model=UploadInitResponse, status_code=201)
async def init_upload(
    body: UploadInitRequest,
    db: AsyncSession = Depends(get_async_db),
) -> UploadInitResponse:
    _validate_mime(body.mime_type)
    if body.file_size_bytes > settings.max_file_size_bytes:
        raise FileTooLargeError(
            f"File size {body.file_size_bytes / 1024 / 1024:.1f} MB exceeds "
            f"the {settings.MAX_FILE_SIZE_MB} MB limit"
        )
    ext = _infer_extension(body.filename, body.mime_type)
    job = Job(
        filename=f"source{ext}",
        original_filename=body.filename,
        file_size_bytes=body.file_size_bytes,
        mime_type=body.mime_type,
        total_chunks=body.total_chunks,
        stage=JobStage.PENDING,
    )
    db.add(job)
    await db.flush()
    await db.commit()
    base = f"{settings.PUBLIC_BASE_URL}/api/v1/uploads/{job.id}"
    return UploadInitResponse(
        job_id=job.id,
        upload_url=f"{base}/file",
        chunk_url_template=f"{base}/chunk",
    )
@router.put("/{job_id}/chunk", response_model=ChunkUploadResponse)
async def upload_chunk(
    job_id: str,
    index: int = Query(..., ge=0, description="Zero-based chunk index"),
    request: Request = None,
    db: AsyncSession = Depends(get_async_db),
) -> ChunkUploadResponse:
    job = await db.get(Job, job_id)
    if job is None:
        raise JobNotFoundError(job_id)
    if job.stage not in (JobStage.PENDING, JobStage.UPLOADING):
        raise JobAlreadyCompletedError(
            f"Job {job_id} is in stage '{job.stage}' — cannot accept more chunks"
        )
    data = await request.body()
    if len(data) == 0:
        raise HTTPException(status_code=400, detail="Empty chunk body")
    if len(data) > CHUNK_SIZE_LIMIT:
        raise FileTooLargeError(f"Chunk exceeds {CHUNK_SIZE_LIMIT // 1024 // 1024} MB limit")
    await save_chunk(job_id, index, data)
    job.stage = JobStage.UPLOADING
    job.chunks_received = (job.chunks_received or 0) + 1
    await db.commit()
    return ChunkUploadResponse(
        job_id=job_id,
        chunk_index=index,
        chunks_received=job.chunks_received,
        total_chunks=job.total_chunks,
        is_complete=False,
    )
@router.post("/{job_id}/complete", response_model=UploadCompleteResponse)
async def complete_chunked_upload(
    job_id: str,
    body: UploadCompleteRequest = UploadCompleteRequest(),
    db: AsyncSession = Depends(get_async_db),
) -> UploadCompleteResponse:
    job = await db.get(Job, job_id)
    if job is None:
        raise JobNotFoundError(job_id)
    if job.stage not in (JobStage.PENDING, JobStage.UPLOADING):
        raise JobAlreadyCompletedError(f"Job {job_id} is already in stage '{job.stage}'")
    total = body.total_chunks or job.total_chunks
    if total is None:
        raise HTTPException(status_code=400, detail="total_chunks is required for chunked uploads")
    _, ext = os.path.splitext(job.filename)
    assembled_path = await assemble_chunks(job_id, total, ext or ".mp4")
    job.file_path = str(assembled_path)
    job.stage = JobStage.UPLOADED
    job.uploaded_at = datetime.now(timezone.utc)
    await db.commit()
    await enqueue_job(job_id)
    return UploadCompleteResponse(
        job_id=job_id,
        stage=JobStage.UPLOADED,
        message="Upload complete — processing started",
    )
@router.post("/{job_id}/file", response_model=UploadCompleteResponse, status_code=202)
async def upload_single_file(
    job_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_async_db),
) -> UploadCompleteResponse:
    job = await db.get(Job, job_id)
    if job is None:
        raise JobNotFoundError(job_id)
    if job.stage not in (JobStage.PENDING, JobStage.UPLOADING):
        raise JobAlreadyCompletedError(f"Job {job_id} is already in stage '{job.stage}'")
    data = await file.read()
    if len(data) > settings.max_file_size_bytes:
        raise FileTooLargeError(
            f"Uploaded file {len(data) / 1024 / 1024:.1f} MB exceeds "
            f"{settings.MAX_FILE_SIZE_MB} MB limit"
        )
    _, ext = os.path.splitext(job.original_filename or file.filename or "video.mp4")
    saved_path = await save_single_upload(job_id, data, ext or ".mp4")
    job.file_path = str(saved_path)
    job.stage = JobStage.UPLOADED
    job.uploaded_at = datetime.now(timezone.utc)
    if file.size:
        job.file_size_bytes = file.size
    await db.commit()
    await enqueue_job(job_id)
    return UploadCompleteResponse(
        job_id=job_id,
        stage=JobStage.UPLOADED,
        message="Upload received — processing started",
    )
@router.delete("/{job_id}", status_code=204)
async def cancel_upload(
    job_id: str,
    db: AsyncSession = Depends(get_async_db),
) -> None:
    job = await db.get(Job, job_id)
    if job is None:
        raise JobNotFoundError(job_id)
    job.stage = JobStage.FAILED
    job.error_message = "Cancelled by client"
    await db.commit()
    await cleanup_job(job_id)
