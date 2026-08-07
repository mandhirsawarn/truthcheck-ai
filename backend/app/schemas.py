from __future__ import annotations
import time
from enum import StrEnum
from typing import Any
from pydantic import BaseModel, ConfigDict, Field
class JobStage(StrEnum):
    PENDING = "pending"
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    VALIDATING = "validating"
    EXTRACTING_FRAMES = "extracting_frames"
    DETECTING_FACES = "detecting_faces"
    RUNNING_INFERENCE = "running_inference"
    AGGREGATING = "aggregating"
    COMPLETED = "completed"
    FAILED = "failed"
class Verdict(StrEnum):
    LIKELY_AI_GENERATED = "likely_ai_generated"
    LIKELY_AUTHENTIC = "likely_authentic"
    INCONCLUSIVE = "inconclusive"
class UploadInitRequest(BaseModel):
    filename: str = Field(..., min_length=1, max_length=255)
    file_size_bytes: int = Field(..., ge=1)
    mime_type: str = Field(default="video/mp4")
    total_chunks: int | None = Field(default=None, ge=1, description="None = single-shot upload")
    sha256: str | None = Field(default=None, description="Optional client-computed hash for integrity")
class UploadInitResponse(BaseModel):
    job_id: str
    upload_url: str
    chunk_url_template: str
    max_chunk_size_bytes: int = 5 * 1024 * 1024
class ChunkUploadResponse(BaseModel):
    job_id: str
    chunk_index: int
    chunks_received: int
    total_chunks: int | None
    is_complete: bool = False
class UploadCompleteRequest(BaseModel):
    total_chunks: int | None = None
class UploadCompleteResponse(BaseModel):
    job_id: str
    stage: JobStage
    message: str = "Processing started"
class StageProgress(BaseModel):
    stage: JobStage
    progress: float = Field(ge=0.0, le=1.0)
    frames_extracted: int | None = None
    frames_total: int | None = None
class JobStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    job_id: str
    filename: str
    stage: JobStage
    stage_progress: float
    error_message: str | None = None
    created_at: str
    uploaded_at: str | None = None
    completed_at: str | None = None
    verdict: Verdict | None = None
    confidence: float | None = None
class FrameScoreSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    frame_index: int
    timestamp_seconds: float
    spatial_score: float
    frequency_score: float
    temporal_score: float
    compression_score: float
    fusion_score: float
    has_face: bool
    blur_score: float
    frame_url: str
class StreamBreakdown(BaseModel):
    spatial: float = Field(description="EfficientNet/CNN deepfake classifier score")
    frequency: float = Field(description="FFT-based GAN frequency artifact score")
    temporal: float = Field(description="Frame-to-frame temporal consistency score")
    compression: float = Field(description="DCT block compression artifact score")
class VideoMetadata(BaseModel):
    duration_seconds: float | None = None
    fps: float | None = None
    width: int | None = None
    height: int | None = None
    codec: str | None = None
    file_size_bytes: int | None = None
class FullResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    job_id: str
    filename: str
    verdict: Verdict
    confidence: float = Field(description="Calibrated probability 0–100")
    stream_breakdown: StreamBreakdown
    explanation_bullets: list[str]
    evidence_frame_urls: list[str]
    model_version: str
    processing_time_ms: int
    frames_analyzed: int
    faces_detected_in: int
    video: VideoMetadata
    frame_scores_url: str
class FrameListResponse(BaseModel):
    job_id: str
    total: int
    page: int
    page_size: int
    frames: list[FrameScoreSchema]
class WSEvent(BaseModel):
    event: str
    job_id: str
    stage: JobStage
    stage_progress: float
    ts: float = Field(default_factory=time.time)
    verdict: Verdict | None = None
    confidence: float | None = None
    error_message: str | None = None
class ErrorResponse(BaseModel):
    code: str
    message: str
    detail: Any = None
class JobListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    jobs: list[JobStatusResponse]
