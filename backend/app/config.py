from pathlib import Path
from typing import Annotated
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/deepfake.db"
    UPLOAD_DIR: Path = Path("./data/uploads")
    MAX_FILE_SIZE_MB: int = Field(default=500, ge=1, le=4096)
    MAX_DURATION_SECONDS: float = Field(default=300.0, ge=10.0)
    ALLOWED_MIME_TYPES: list[str] = [
        "video/mp4",
        "video/quicktime",
        "video/x-msvideo",
        "video/x-matroska",
        "video/webm",
        "video/mpeg",
        "video/3gpp",
        "video/ogg",
        "application/octet-stream",
    ]
    WORKER_CONCURRENCY: int = Field(default=2, ge=1, le=8)
    FRAME_SAMPLE_COUNT: int = Field(default=20, ge=5, le=60)
    MODEL_NAME: str = "prithivMLmods/Deep-Fake-Detector-v2-Model"
    FALLBACK_MODEL_NAME: str = "prithivMLmods/Deep-Fake-Detector-v2-Model"
    MODEL_DEVICE: str = "auto"
    ENABLE_FREQUENCY_ANALYSIS: bool = True
    ENABLE_TEMPORAL_ANALYSIS: bool = True
    ENABLE_COMPRESSION_ANALYSIS: bool = True
    ENABLE_AUDIO_ANALYSIS: bool = True
    FACE_CROP_MARGIN: float = Field(default=0.5, ge=0.0, le=2.0)
    MODEL_FAKE_GAMMA: dict[str, float] = {
        "dima806/deepfake_vs_real_image_detection": 0.5,
        "prithivMLmods/Deep-Fake-Detector-v2-Model": 1.0,
        "local-efficientnet-b0": 1.0,
    }
    NON_FACE_FRAME_WEIGHT: float = Field(default=0.1, ge=0.0, le=1.0)
    WEIGHT_SPATIAL: float = Field(default=0.55, ge=0.0, le=1.0)
    WEIGHT_FREQUENCY: float = Field(default=0.10, ge=0.0, le=1.0)
    WEIGHT_TEMPORAL: float = Field(default=0.15, ge=0.0, le=1.0)
    WEIGHT_COMPRESSION: float = Field(default=0.10, ge=0.0, le=1.0)
    WEIGHT_AUDIO: float = Field(default=0.10, ge=0.0, le=1.0)
    THRESHOLD_AI_GENERATED: float = Field(default=0.55, ge=0.5, le=1.0)
    THRESHOLD_AUTHENTIC: float = Field(default=0.35, ge=0.0, le=0.5)
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    PUBLIC_BASE_URL: str = "http://localhost:8000"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    LOG_JSON: bool = False
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 30
    @field_validator("UPLOAD_DIR", mode="before")
    @classmethod
    def _make_upload_dir(cls, v: str | Path) -> Path:
        p = Path(v)
        p.mkdir(parents=True, exist_ok=True)
        return p
    @property
    def max_file_size_bytes(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024
    @property
    def db_data_dir(self) -> Path:
        d = Path("./data")
        d.mkdir(parents=True, exist_ok=True)
        return d
settings = Settings()
