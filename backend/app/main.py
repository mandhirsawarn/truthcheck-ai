from __future__ import annotations
import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path
import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.db import create_all_tables
from app.exceptions import DeepfakeAPIError
from app.middleware import RateLimitMiddleware, RequestIDMiddleware, TimingMiddleware
from app.routers import analyze, status, websocket, results, uploads
from app.worker import start_worker_pool, stop_worker_pool
def _setup_logging() -> None:
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    if settings.LOG_JSON:
        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.JSONRenderer(),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(level),
            logger_factory=structlog.PrintLoggerFactory(sys.stdout),
        )
    else:
        logging.basicConfig(
            level=level,
            format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
            datefmt="%H:%M:%S",
        )
_setup_logging()
logger = logging.getLogger(__name__)
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Deepfake Detection API")
    await create_all_tables()
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("Database tables ready: %s", settings.DATABASE_URL)
    await start_worker_pool()
    logger.info(
        "Server ready — workers=%d upload_dir=%s",
        settings.WORKER_CONCURRENCY,
        settings.UPLOAD_DIR,
    )
    yield
    logger.info("Shutting down worker pool...")
    await stop_worker_pool()
    logger.info("Shutdown complete")
app = FastAPI(
    title="Deepfake Video Detection API",
    description=(
        "Production-grade deepfake and AI-generated video detection. "
        "Multi-stream ensemble: spatial CNN + frequency FFT + temporal consistency + compression analysis."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(TimingMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.exception_handler(DeepfakeAPIError)
async def handle_api_error(request: Request, exc: DeepfakeAPIError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content=exc.to_dict())
@app.exception_handler(404)
async def handle_404(request: Request, exc) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"code": "not_found", "message": "The requested resource does not exist."},
    )
@app.exception_handler(500)
async def handle_500(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"code": "internal_error", "message": "An unexpected error occurred."},
    )
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=str(settings.UPLOAD_DIR)), name="media")
API_PREFIX = "/api/v1"
app.include_router(uploads.router, prefix=API_PREFIX)
app.include_router(status.router, prefix=API_PREFIX)
app.include_router(results.router, prefix=API_PREFIX)
app.include_router(websocket.router, prefix=API_PREFIX)
app.include_router(analyze.router, prefix=API_PREFIX)
@app.get("/health", tags=["health"])
@app.get("/api/v1/health", tags=["health"])
async def health() -> dict:
    return {"status": "ok", "version": "1.0.0"}
@app.get("/api/v1/info", tags=["health"])
async def info() -> dict:
    from app.worker import get_queue
    return {
        "status": "ok",
        "version": "1.0.0",
        "worker_concurrency": settings.WORKER_CONCURRENCY,
        "queue_depth": get_queue().qsize(),
        "features": {
            "frequency_analysis": settings.ENABLE_FREQUENCY_ANALYSIS,
            "temporal_analysis": settings.ENABLE_TEMPORAL_ANALYSIS,
            "compression_analysis": settings.ENABLE_COMPRESSION_ANALYSIS,
            "audio_analysis": settings.ENABLE_AUDIO_ANALYSIS,
        },
        "limits": {
            "max_file_size_mb": settings.MAX_FILE_SIZE_MB,
            "max_duration_seconds": settings.MAX_DURATION_SECONDS,
        },
        "thresholds": {
            "ai_generated": settings.THRESHOLD_AI_GENERATED,
            "authentic": settings.THRESHOLD_AUTHENTIC,
        },
    }
