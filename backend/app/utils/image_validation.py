"""
Section 27: only accept JPG/PNG/WEBP, validate real dimensions (not just
the filename extension), and re-encode server-side before storage — this
also strips EXIF metadata and normalizes orientation, so what we store
is never the client's raw, unexamined bytes.
"""

import io

from fastapi import UploadFile
from PIL import Image, ImageOps

from app.core.exceptions import ImageValidationError

MAX_UPLOAD_BYTES = 8 * 1024 * 1024  # 8 MB
MIN_DIMENSION = 200
MAX_DIMENSION = 6000
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}
_READ_CHUNK_BYTES = 1024 * 1024  # 1 MB


async def read_upload_with_limit(file: UploadFile, max_bytes: int = MAX_UPLOAD_BYTES) -> bytes:
    """
    Reads an upload in bounded chunks and aborts as soon as max_bytes is
    exceeded, instead of `await file.read()` — which would buffer the
    entire body (however large an attacker sends it) before any size
    check ever runs. This is the actual enforcement point; the size
    check inside validate_and_normalize_image is now a redundant
    belt-and-suspenders check for callers that already have full bytes.
    """
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = await file.read(_READ_CHUNK_BYTES)
        if not chunk:
            break
        total += len(chunk)
        if total > max_bytes:
            raise ImageValidationError(
                f"Image is too large. Maximum size is {max_bytes // (1024 * 1024)} MB."
            )
        chunks.append(chunk)
    return b"".join(chunks)


def validate_and_normalize_image(raw_bytes: bytes) -> bytes:
    if len(raw_bytes) > MAX_UPLOAD_BYTES:
        raise ImageValidationError("Image is too large. Maximum size is 8 MB.")

    try:
        image = Image.open(io.BytesIO(raw_bytes))
        image.verify()  # cheap corruption check
        # verify() leaves the file object unusable for further reads —
        # reopen to actually process it.
        image = Image.open(io.BytesIO(raw_bytes))
    except Exception:
        raise ImageValidationError(
            "This doesn't look like a valid image file. Please upload a JPG, PNG, or WEBP."
        )

    if image.format not in ALLOWED_FORMATS:
        raise ImageValidationError("Please upload a JPG, PNG, or WEBP image.")

    width, height = image.size
    if width < MIN_DIMENSION or height < MIN_DIMENSION:
        raise ImageValidationError(
            f"Image is too small. Please upload a photo at least {MIN_DIMENSION}x{MIN_DIMENSION}px."
        )
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise ImageValidationError("Image dimensions are too large.")

    # Respect the camera's rotation metadata, then drop the metadata
    # entirely by re-encoding as a fresh JPEG.
    normalized = ImageOps.exif_transpose(image).convert("RGB")
    buffer = io.BytesIO()
    normalized.save(buffer, format="JPEG", quality=90)
    return buffer.getvalue()
