import io

import pytest
from PIL import Image

from app.core.exceptions import ImageValidationError
from app.utils.image_validation import MAX_UPLOAD_BYTES, validate_and_normalize_image


def _jpeg_bytes(width: int, height: int) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (width, height), color=(120, 120, 120)).save(buffer, format="JPEG")
    return buffer.getvalue()


def test_accepts_and_reencodes_a_valid_photo():
    normalized = validate_and_normalize_image(_jpeg_bytes(400, 600))
    reopened = Image.open(io.BytesIO(normalized))
    assert reopened.format == "JPEG"
    assert reopened.size == (400, 600)


def test_rejects_non_image_bytes():
    with pytest.raises(ImageValidationError):
        validate_and_normalize_image(b"this is not an image")


def test_rejects_image_below_minimum_dimensions():
    with pytest.raises(ImageValidationError, match="too small"):
        validate_and_normalize_image(_jpeg_bytes(50, 50))


def test_rejects_oversized_upload():
    oversized = b"\xff\xd8\xff\xe0" + b"0" * (MAX_UPLOAD_BYTES + 1)
    with pytest.raises(ImageValidationError, match="too large"):
        validate_and_normalize_image(oversized)
