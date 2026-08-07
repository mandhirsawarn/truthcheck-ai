from __future__ import annotations
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import AsyncSessionLocal
from app.exceptions import JobNotFoundError
from app.models import Job
from app.schemas import JobStage, Verdict, WSEvent
from app.ws_manager import ws_manager
logger = logging.getLogger(__name__)
router = APIRouter(tags=["websocket"])
@router.websocket("/ws/{job_id}")
async def websocket_job_status(websocket: WebSocket, job_id: str) -> None:
    await ws_manager.connect(job_id, websocket)
    logger.debug("WS client connected: job=%s", job_id)
    try:
        async with AsyncSessionLocal() as db:
            job: Job | None = await db.get(Job, job_id)
            if job is None:
                await websocket.send_json({
                    "event": "error",
                    "job_id": job_id,
                    "error": "job_not_found",
                    "message": f"Job '{job_id}' does not exist",
                })
                await websocket.close(code=4404)
                return
            if job.stage == JobStage.COMPLETED and job.result:
                await websocket.send_text(
                    WSEvent(
                        event="completed",
                        job_id=job_id,
                        stage=JobStage.COMPLETED,
                        stage_progress=1.0,
                        verdict=Verdict(job.result.verdict),
                        confidence=job.result.confidence,
                    ).model_dump_json()
                )
            elif job.stage == JobStage.FAILED:
                await websocket.send_text(
                    WSEvent(
                        event="failed",
                        job_id=job_id,
                        stage=JobStage.FAILED,
                        stage_progress=job.stage_progress,
                        error_message=job.error_message,
                    ).model_dump_json()
                )
            else:
                await websocket.send_text(
                    WSEvent(
                        event="stage_change",
                        job_id=job_id,
                        stage=JobStage(job.stage),
                        stage_progress=job.stage_progress,
                    ).model_dump_json()
                )
        while True:
            try:
                msg = await websocket.receive_text()
                if msg == "ping":
                    await websocket.send_text("pong")
            except WebSocketDisconnect:
                break
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.warning("WebSocket error for job=%s: %s", job_id, e)
    finally:
        ws_manager.disconnect(job_id, websocket)
        logger.debug("WS client disconnected: job=%s", job_id)
