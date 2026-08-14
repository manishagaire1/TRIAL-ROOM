"""
Section 26: baseline security headers on every response. This is a pure
JSON + image API (no HTML templates), so a strict Content-Security-Policy
is safe everywhere except FastAPI's own interactive docs, which load
Swagger UI's JS/CSS from a CDN — those paths are excluded from the CSP
so `/docs` keeps working, while X-Content-Type-Options and
X-Frame-Options still apply everywhere.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

_DOCS_PATHS = {"/docs", "/redoc", "/openapi.json"}


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        if request.url.path not in _DOCS_PATHS:
            response.headers["Content-Security-Policy"] = "default-src 'none'"
        return response
