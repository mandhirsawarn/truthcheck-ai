from __future__ import annotations
import asyncio
import logging
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import select
from app.config import settings
from app.db import AsyncSessionLocal
from app.exceptions import PipelineError, VideoValidationError
from app.models import AnalysisResult, FrameScore, Job
from app.schemas import JobStage, Verdict, WSEvent
from app.storage import frame_url, cleanup_source_and_frames
from app.ws_manager import ws_manager
if TYPE_CHECKING:
    pass
logger = logging.getLogger(__name__)
_job_queue: asyncio.Queue[str] = asyncio.Queue()
_executor: ThreadPoolExecutor | None = None
_worker_tasks: list[asyncio.Task] = []
def get_queue() -> asyncio.Queue[str]:
    return _job_queue
async def _update_stage(
    job_id: str,
    stage: JobStage,
    progress: float = 0.0,
    error_message: str | None = None,
) -> None:
    async with AsyncSessionLocal() as db:
        job = await db.get(Job, job_id)
        if job is None:
            return
        job.stage = stage
        job.stage_progress = progress
        if error_message is not None:
            job.error_message = error_message
        if stage == JobStage.COMPLETED:
            job.completed_at = datetime.now(timezone.utc)
        await db.commit()
    event = WSEvent(
        event="stage_change" if stage not in (JobStage.COMPLETED, JobStage.FAILED) else stage,
        job_id=job_id,
        stage=stage,
        stage_progress=progress,
        error_message=error_message,
    )
    await ws_manager.broadcast(job_id, event)
async def _update_progress(job_id: str, stage: JobStage, progress: float) -> None:
    async with AsyncSessionLocal() as db:
        job = await db.get(Job, job_id)
        if job:
            job.stage_progress = progress
            await db.commit()
    await ws_manager.broadcast(
        job_id,
        WSEvent(event="progress", job_id=job_id, stage=stage, stage_progress=progress),
    )
async def _run_pipeline(job_id: str) -> None:
    loop = asyncio.get_event_loop()
    async with AsyncSessionLocal() as db:
        job = await db.get(Job, job_id)
        if job is None:
            logger.error("Worker picked up unknown job_id=%s", job_id)
            return
        video_path = job.file_path
        filename = job.filename
        file_size = job.file_size_bytes
    if not video_path:
        await _update_stage(job_id, JobStage.FAILED, error_message="No video file path on job record")
        return
    pipeline_start = time.monotonic()
    try:
        await _update_stage(job_id, JobStage.VALIDATING, 0.0)
        from app.pipeline.extract_frames import validate_video
        metadata = await loop.run_in_executor(
            _executor, validate_video, video_path, settings.MAX_DURATION_SECONDS
        )
        await _update_stage(job_id, JobStage.VALIDATING, 1.0)
        await _update_stage(job_id, JobStage.EXTRACTING_FRAMES, 0.0)
        from app.pipeline.extract_frames import extract_frames, extract_audio
        def _extract_all():
            frames = extract_frames(video_path, job_id, metadata)
            audio_path = extract_audio(video_path, job_id)
            return frames, audio_path
        frames, audio_path = await loop.run_in_executor(_executor, _extract_all)
        await _update_stage(job_id, JobStage.EXTRACTING_FRAMES, 1.0)
        await _update_stage(job_id, JobStage.DETECTING_FACES, 0.0)
        from app.pipeline.face_detect import detect_faces_batch
        frames = await loop.run_in_executor(
            _executor,
            detect_faces_batch,
            frames,
            lambda i, n: None,
        )
        await _update_stage(job_id, JobStage.DETECTING_FACES, 1.0)
        await _update_stage(job_id, JobStage.RUNNING_INFERENCE, 0.0)
        from app.pipeline.inference import score_frames_ensemble
        total_frames = len(frames)
        def _inference_with_progress():
            return score_frames_ensemble(frames, audio_path=audio_path)
        scored_frames = await loop.run_in_executor(_executor, _inference_with_progress)
        await _update_stage(job_id, JobStage.RUNNING_INFERENCE, 1.0)
        await _update_stage(job_id, JobStage.AGGREGATING, 0.0)
        from app.pipeline.aggregate import aggregate_ensemble
        aggregated = aggregate_ensemble(
            scored_frames=scored_frames,
            metadata=metadata,
            job_id=job_id,
        )
        processing_ms = int((time.monotonic() - pipeline_start) * 1000)
        try:
            from app.pipeline.inference import get_loaded_model_version
            model_version = get_loaded_model_version()
        except Exception:
            model_version = "1.0.0"
        async with AsyncSessionLocal() as db:
            result = AnalysisResult(
                job_id=job_id,
                verdict=aggregated["verdict"],
                confidence=aggregated["confidence"],
                spatial_confidence=aggregated["spatial_confidence"],
                frequency_confidence=aggregated["frequency_confidence"],
                temporal_confidence=aggregated["temporal_confidence"],
                compression_confidence=aggregated["compression_confidence"],
                model_version=model_version,
                processing_time_ms=processing_ms,
                frames_analyzed=len(scored_frames),
                faces_detected_in=sum(1 for f in scored_frames if f.get("has_face")),
                video_duration_seconds=metadata.get("duration"),
                video_fps=metadata.get("fps"),
                video_width=metadata.get("width"),
                video_height=metadata.get("height"),
                video_codec=metadata.get("codec"),
                explanation_bullets=aggregated["explanation_bullets"],
                evidence_frame_urls=aggregated["evidence_frame_urls"],
            )
            db.add(result)
            await db.flush()
            for sf in scored_frames:
                db.add(FrameScore(
                    result_id=result.id,
                    frame_index=sf["frame_index"],
                    timestamp_seconds=sf["timestamp"],
                    spatial_score=sf.get("spatial_score", 0.0),
                    frequency_score=sf.get("frequency_score", 0.0),
                    temporal_score=sf.get("temporal_score", 0.0),
                    compression_score=sf.get("compression_score", 0.0),
                    fusion_score=sf["fusion_score"],
                    has_face=sf.get("has_face", False),
                    blur_score=sf.get("blur_score", 1.0),
                    frame_filename=sf["filename"],
                ))
            job = await db.get(Job, job_id)
            job.stage = JobStage.COMPLETED
            job.stage_progress = 1.0
            job.completed_at = datetime.now(timezone.utc)
            await db.commit()
        await ws_manager.broadcast(
            job_id,
            WSEvent(
                event="completed",
                job_id=job_id,
                stage=JobStage.COMPLETED,
                stage_progress=1.0,
                verdict=Verdict(aggregated["verdict"]),
                confidence=aggregated["confidence"],
            ),
        )
        logger.info(
            "Pipeline completed: job=%s verdict=%s confidence=%.1f%% duration_ms=%d",
            job_id,
            aggregated["verdict"],
            aggregated["confidence"],
            processing_ms,
        )
        try:
            pass
        except Exception:
            pass
    except Exception as exc:
        logger.error("Pipeline failed for job=%s:\n%s", job_id, traceback.format_exc())
        err_msg = str(exc)
        await _update_stage(job_id, JobStage.FAILED, error_message=err_msg)
async def _worker(worker_id: int) -> None:
    logger.info("Pipeline worker %d started", worker_id)
    while True:
        job_id = await _job_queue.get()
        try:
            logger.info("Worker %d processing job=%s", worker_id, job_id)
            await _run_pipeline(job_id)
        except Exception:
            logger.exception("Unhandled error in worker %d", worker_id)
        finally:
            _job_queue.task_done()
async def start_worker_pool() -> None:
    global _executor, _worker_tasks
    _executor = ThreadPoolExecutor(
        max_workers=settings.WORKER_CONCURRENCY,
        thread_name_prefix="pipeline",
    )
    for i in range(settings.WORKER_CONCURRENCY):
        task = asyncio.create_task(_worker(i), name=f"pipeline-worker-{i}")
        _worker_tasks.append(task)
    logger.info("Started %d pipeline worker(s)", settings.WORKER_CONCURRENCY)
async def stop_worker_pool() -> None:
    global _executor
    for task in _worker_tasks:
        task.cancel()
    _worker_tasks.clear()
    if _executor:
        _executor.shutdown(wait=True)
    logger.info("Pipeline worker pool stopped")
async def enqueue_job(job_id: str) -> None:
    await _job_queue.put(job_id)
    logger.debug("Enqueued job=%s queue_size=%d", job_id, _job_queue.qsize())
