import uuid
from datetime import datetime, timezone
from typing import Any
from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base
def _uuid() -> str:
    return str(uuid.uuid4())
def _now() -> datetime:
    return datetime.now(timezone.utc)
class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    filename: Mapped[str] = mapped_column(Text, nullable=False)
    original_filename: Mapped[str] = mapped_column(Text, nullable=False)
    file_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(128), nullable=True)
    total_chunks: Mapped[int | None] = mapped_column(Integer, nullable=True)
    chunks_received: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    stage: Mapped[str] = mapped_column(
        String(32), nullable=False, default="pending", index=True
    )
    stage_progress: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=_now, onupdate=_now, nullable=True
    )
    uploaded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    investigation_status: Mapped[str] = mapped_column(
        String(32), default="Needs Review", nullable=False, index=True
    )
    investigation_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    result: Mapped["AnalysisResult | None"] = relationship(
        "AnalysisResult", back_populates="job", uselist=False, lazy="selectin"
    )
    @property
    def is_terminal(self) -> bool:
        return self.stage in ("completed", "failed")
    @property
    def is_done(self) -> bool:
        return self.stage == "completed"
class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    job_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    verdict: Mapped[str] = mapped_column(String(32), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    spatial_confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    frequency_confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    temporal_confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    compression_confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    model_version: Mapped[str] = mapped_column(Text, nullable=False, default="1.0.0")
    processing_time_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    frames_analyzed: Mapped[int] = mapped_column(Integer, nullable=False)
    faces_detected_in: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    video_duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    video_fps: Mapped[float | None] = mapped_column(Float, nullable=True)
    video_width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    video_height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    video_codec: Mapped[str | None] = mapped_column(String(64), nullable=True)
    explanation_bullets: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    evidence_frame_urls: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, nullable=False
    )
    job: Mapped["Job"] = relationship("Job", back_populates="result")
    frame_scores: Mapped[list["FrameScore"]] = relationship(
        "FrameScore", back_populates="result", lazy="noload"
    )
class FrameScore(Base):
    __tablename__ = "frame_scores"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    result_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("analysis_results.id", ondelete="CASCADE"), nullable=False, index=True
    )
    frame_index: Mapped[int] = mapped_column(Integer, nullable=False)
    timestamp_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    spatial_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    frequency_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    temporal_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    compression_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    fusion_score: Mapped[float] = mapped_column(Float, nullable=False)
    has_face: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    blur_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    frame_filename: Mapped[str] = mapped_column(Text, nullable=False)
    result: Mapped["AnalysisResult"] = relationship(
        "AnalysisResult", back_populates="frame_scores"
    )
