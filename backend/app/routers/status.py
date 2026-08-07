from __future__ import annotations
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_async_db
from app.exceptions import JobNotFoundError
from app.models import AnalysisResult, Job
from app.schemas import JobListResponse, JobStage, JobStatusResponse, Verdict
router = APIRouter(tags=["jobs"])
def _job_to_status(job: Job) -> JobStatusResponse:
    result = job.result
    return JobStatusResponse(
        job_id=job.id,
        filename=job.original_filename,
        stage=JobStage(job.stage),
        stage_progress=job.stage_progress,
        error_message=job.error_message,
        created_at=job.created_at.isoformat(),
        uploaded_at=job.uploaded_at.isoformat() if job.uploaded_at else None,
        completed_at=job.completed_at.isoformat() if job.completed_at else None,
        verdict=Verdict(result.verdict) if result else None,
        confidence=result.confidence if result else None,
    )
@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str,
    db: AsyncSession = Depends(get_async_db),
) -> JobStatusResponse:
    job = await db.get(Job, job_id)
    if job is None:
        raise JobNotFoundError(job_id)
    return _job_to_status(job)
@router.get("/jobs", response_model=JobListResponse)
async def list_jobs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    stage: str | None = Query(default=None, description="Filter by stage"),
    db: AsyncSession = Depends(get_async_db),
) -> JobListResponse:
    q = select(Job)
    if stage:
        q = q.where(Job.stage == stage)
    count_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(count_q)).scalar_one()
    q = q.order_by(Job.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    jobs = (await db.execute(q)).scalars().all()
    return JobListResponse(
        total=total,
        page=page,
        page_size=page_size,
        jobs=[_job_to_status(j) for j in jobs],
    )
