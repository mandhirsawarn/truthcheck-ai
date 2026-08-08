from __future__ import annotations
import json
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse, Response
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_async_db
from app.exceptions import JobNotFoundError, ResultNotReadyError
from app.models import AnalysisResult, FrameScore, Job
from app.schemas import (
FrameListResponse,
FrameScoreSchema,
FullResultResponse,
JobStage,
StreamBreakdown,
Verdict,
VideoMetadata,
UpdateInvestigationRequest,
)
from app.storage import frame_url
from app.config import settings
router = APIRouter(prefix="/results", tags=["results"])
async def _get_result_or_raise(job_id: str, db: AsyncSession) -> tuple[Job, AnalysisResult]:
    job = await db.get(Job, job_id)
    if job is None:
        raise JobNotFoundError(job_id)
    if job.stage != JobStage.COMPLETED or job.result is None:
        raise ResultNotReadyError(job_id, job.stage)
    return job, job.result
@router.get("/{job_id}", response_model=FullResultResponse)
async def get_full_result(
    job_id: str,
    db: AsyncSession = Depends(get_async_db),
) -> FullResultResponse:
    job, result = await _get_result_or_raise(job_id, db)
    return FullResultResponse(
        job_id=job_id,
        filename=job.original_filename,
        verdict=Verdict(result.verdict),
        confidence=result.confidence,
        stream_breakdown=StreamBreakdown(
            spatial=result.spatial_confidence,
            frequency=result.frequency_confidence,
            temporal=result.temporal_confidence,
            compression=result.compression_confidence,
        ),
        explanation_bullets=result.explanation_bullets,
        evidence_frame_urls=result.evidence_frame_urls,
        model_version=result.model_version,
        processing_time_ms=result.processing_time_ms,
        frames_analyzed=result.frames_analyzed,
        faces_detected_in=result.faces_detected_in,
        video=VideoMetadata(
            duration_seconds=result.video_duration_seconds,
            fps=result.video_fps,
            width=result.video_width,
            height=result.video_height,
            codec=result.video_codec,
            file_size_bytes=job.file_size_bytes,
        ),
        frame_scores_url=f"{settings.PUBLIC_BASE_URL}/api/v1/results/{job_id}/frames",
        investigation_status=job.investigation_status,
        investigation_notes=job.investigation_notes,
    )
@router.get("/{job_id}/frames", response_model=FrameListResponse)
async def get_frame_scores(
    job_id: str,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_async_db),
) -> FrameListResponse:
    job, result = await _get_result_or_raise(job_id, db)
    count_q = select(func.count()).where(FrameScore.result_id == result.id)
    total = (await db.execute(count_q)).scalar_one()
    q = (
        select(FrameScore)
        .where(FrameScore.result_id == result.id)
        .order_by(FrameScore.frame_index)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    frames = (await db.execute(q)).scalars().all()
    frame_schemas = [
        FrameScoreSchema(
            frame_index=f.frame_index,
            timestamp_seconds=f.timestamp_seconds,
            spatial_score=f.spatial_score,
            frequency_score=f.frequency_score,
            temporal_score=f.temporal_score,
            compression_score=f.compression_score,
            fusion_score=f.fusion_score,
            has_face=f.has_face,
            blur_score=f.blur_score,
            frame_url=frame_url(job_id, f.frame_filename),
        )
        for f in frames
    ]
    return FrameListResponse(
        job_id=job_id,
        total=total,
        page=page,
        page_size=page_size,
        frames=frame_schemas,
    )
@router.get("/{job_id}/export")
async def export_result(
    job_id: str,
    db: AsyncSession = Depends(get_async_db),
) -> Response:
    job, result = await _get_result_or_raise(job_id, db)
    q = select(FrameScore).where(FrameScore.result_id == result.id).order_by(FrameScore.frame_index)
    frames = (await db.execute(q)).scalars().all()
    report = {
        "report_version": "1.0",
        "job_id": job_id,
        "filename": job.original_filename,
        "verdict": result.verdict,
        "confidence": result.confidence,
        "stream_breakdown": {
            "spatial": result.spatial_confidence,
            "frequency": result.frequency_confidence,
            "temporal": result.temporal_confidence,
            "compression": result.compression_confidence,
        },
        "explanation_bullets": result.explanation_bullets,
        "model_version": result.model_version,
        "processing": {
            "time_ms": result.processing_time_ms,
            "frames_analyzed": result.frames_analyzed,
            "faces_detected_in": result.faces_detected_in,
        },
        "video_metadata": {
            "duration_seconds": result.video_duration_seconds,
            "fps": result.video_fps,
            "width": result.video_width,
            "height": result.video_height,
            "codec": result.video_codec,
            "file_size_bytes": job.file_size_bytes,
        },
        "evidence_frame_urls": result.evidence_frame_urls,
        "frame_scores": [
            {
                "frame_index": f.frame_index,
                "timestamp_seconds": f.timestamp_seconds,
                "spatial_score": f.spatial_score,
                "frequency_score": f.frequency_score,
                "temporal_score": f.temporal_score,
                "compression_score": f.compression_score,
                "fusion_score": f.fusion_score,
                "has_face": f.has_face,
                "blur_score": f.blur_score,
                "frame_url": frame_url(job_id, f.frame_filename),
            }
            for f in frames
        ],
        "created_at": result.created_at.isoformat(),
        "investigation_status": job.investigation_status,
        "investigation_notes": job.investigation_notes,
    }
    return Response(
        content=json.dumps(report, indent=2),
        media_type="application/json",
        headers={
            "Content-Disposition": f'attachment; filename="deepfake_report_{job_id[:8]}.json"'
        },
    )

@router.patch("/{job_id}/investigation", response_model=FullResultResponse)
async def update_investigation(
    job_id: str,
    update_data: UpdateInvestigationRequest,
    db: AsyncSession = Depends(get_async_db),
) -> FullResultResponse:
    job, result = await _get_result_or_raise(job_id, db)
    job.investigation_status = update_data.investigation_status
    if update_data.investigation_notes is not None:
        job.investigation_notes = update_data.investigation_notes
    await db.commit()
    await db.refresh(job)
    return await get_full_result(job_id, db)
