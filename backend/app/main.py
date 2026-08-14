import logging

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import (
    auth,
    clothes,
    outfits,
    photo,
    profile,
    size_recommendation,
    style_recommendation,
    tryon,
    users,
    wardrobe,
)
from app.core.config import settings
from app.core.rate_limit import RateLimitMiddleware
from app.core.security_headers import SecurityHeadersMiddleware

logger = logging.getLogger("virtualfit")

app = FastAPI(title="VirtualFit AI API")

# Middleware order matters: Starlette runs them in reverse of add order
# (last added = outermost = runs first). Rate limiting first so an
# over-limit request never reaches CORS/routing; headers last so they
# still land on the 429 responses rate limiting produces.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)

# Every error response uses the same { error: { code, message } } shape
# (docs/05-api-design.md) so the frontend never has to special-case which
# kind of failure it got.

_STATUS_CODES = {
    status.HTTP_400_BAD_REQUEST: "BAD_REQUEST",
    status.HTTP_401_UNAUTHORIZED: "UNAUTHORIZED",
    status.HTTP_403_FORBIDDEN: "FORBIDDEN",
    status.HTTP_404_NOT_FOUND: "NOT_FOUND",
    status.HTTP_409_CONFLICT: "CONFLICT",
}


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    code = _STATUS_CODES.get(exc.status_code, "ERROR")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": code, "message": exc.detail}},
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Some fields are invalid.",
                # jsonable_encoder, not raw exc.errors() — a ValueError
                # raised inside a @model_validator ends up embedded as a
                # live exception object in the error's `ctx`, which the
                # default JSON encoder can't serialize on its own.
                "fields": jsonable_encoder(exc.errors()),
            }
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Section 36: never leak stack traces or internal error detail to the
    # client. The real exception still goes to the server log.
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "Something went wrong. Please try again.",
            }
        },
    )


app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(profile.router, prefix="/api")
app.include_router(clothes.router, prefix="/api")
app.include_router(photo.router, prefix="/api")
app.include_router(tryon.router, prefix="/api")
app.include_router(size_recommendation.router, prefix="/api")
app.include_router(style_recommendation.router, prefix="/api")
app.include_router(outfits.router, prefix="/api")
app.include_router(wardrobe.router, prefix="/api")


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
