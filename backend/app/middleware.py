from __future__ import annotations
import time
import uuid
from collections import defaultdict
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from app.config import settings
class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000
        response.headers["X-Process-Time"] = f"{elapsed_ms:.2f}ms"
        return response
class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self._buckets: dict[str, dict] = defaultdict(
            lambda: {"tokens": settings.RATE_LIMIT_REQUESTS_PER_MINUTE, "last_refill": time.time()}
        )
        self._rate_per_second = settings.RATE_LIMIT_REQUESTS_PER_MINUTE / 60.0
    def _get_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path in ("/health", "/api/v1/health") or request.url.path.startswith("/media"):
            return await call_next(request)
        ip = self._get_client_ip(request)
        bucket = self._buckets[ip]
        now = time.time()
        elapsed = now - bucket["last_refill"]
        bucket["tokens"] = min(
            settings.RATE_LIMIT_REQUESTS_PER_MINUTE,
            bucket["tokens"] + elapsed * self._rate_per_second,
        )
        bucket["last_refill"] = now
        if bucket["tokens"] < 1:
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=429,
                content={
                    "code": "rate_limit_exceeded",
                    "message": "Too many requests. Please slow down.",
                    "detail": {"limit_per_minute": settings.RATE_LIMIT_REQUESTS_PER_MINUTE},
                },
                headers={"Retry-After": "5"},
            )
        bucket["tokens"] -= 1
        return await call_next(request)
