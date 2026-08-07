from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_async_db
router = APIRouter(tags=["analyze"])
@router.get("/analyze")
async def analyze_info():
    return {
        "message": "Use POST /api/v1/uploads/init to start a new analysis.",
        "docs": "/docs",
        "flow": [
            "POST /api/v1/uploads/init — get job_id and upload URL",
            "POST /api/v1/uploads/{job_id}/file — upload video (single-shot)",
            "  OR PUT /api/v1/uploads/{job_id}/chunk?index=N × N chunks",
            "  then POST /api/v1/uploads/{job_id}/complete",
            "Connect to ws://.../api/v1/ws/{job_id} for live updates",
            "OR poll GET /api/v1/jobs/{job_id}",
            "GET /api/v1/results/{job_id} for full result",
        ],
    }
