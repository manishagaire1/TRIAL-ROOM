"""
Section 26 / docs/06: per-IP limits on /auth/* (brute force / spam
signups) and POST /tryon (the AI-generation endpoint — the expensive
resource to abuse).

This is an in-memory fixed-window limiter — correct and sufficient for a
single-process deployment (which is what this project targets), but it
resets on restart and doesn't share state across multiple worker
processes. A production deployment running several workers would need a
shared store (e.g. Redis) instead; noted here rather than silently
assumed away.
"""

import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

_WINDOW_SECONDS = 60
_LIMITS = {
    "auth": 20,  # register + login + guest combined, per IP per minute
    "tryon": 10,  # POST /api/tryon, per IP per minute
}

_buckets: dict[str, list[float]] = defaultdict(list)


def _bucket_name(path: str, method: str) -> str | None:
    # Browsers send an automatic OPTIONS preflight before most real
    # requests — counting those would silently halve the real budget
    # for actual login/signup/try-on attempts.
    if method == "OPTIONS":
        return None
    if path.startswith("/api/auth/"):
        return "auth"
    if path == "/api/tryon" and method == "POST":
        return "tryon"
    return None


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        bucket = _bucket_name(request.url.path, request.method)
        if bucket is not None:
            client_ip = request.client.host if request.client else "unknown"
            key = f"{bucket}:{client_ip}"
            now = time.monotonic()
            window_start = now - _WINDOW_SECONDS

            timestamps = _buckets[key]
            while timestamps and timestamps[0] < window_start:
                timestamps.pop(0)

            if len(timestamps) >= _LIMITS[bucket]:
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": {
                            "code": "RATE_LIMITED",
                            "message": "Too many requests. Please wait a moment and try again.",
                        }
                    },
                )
            timestamps.append(now)

        return await call_next(request)
