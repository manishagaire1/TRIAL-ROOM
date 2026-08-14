"""
Local-disk storage backend. docs/03-architecture.md describes this as one
interface with a swappable implementation — local disk in dev, an
S3-compatible bucket in prod (STORAGE_BACKEND env var). Only "local" is
implemented so far; a future storage_s3.py would offer the same three
functions and main.py/services would pick one based on settings.

Every file is served through an authenticated, ownership-checked API
route (see app/api/photo.py, app/api/tryon.py) — nothing under storage/
is ever exposed as a public static folder (docs/06, Section 25).
"""

import uuid
from pathlib import Path

STORAGE_ROOT = Path(__file__).resolve().parent.parent.parent / "storage"


def _full_path(key: str) -> Path:
    return STORAGE_ROOT / key


def save_bytes(subdir: str, extension: str, data: bytes) -> str:
    """Writes data under storage/<subdir>/<random-uuid>.<extension> and
    returns that relative key. The filename is always server-generated —
    never derived from the client's original filename (docs/06)."""
    directory = STORAGE_ROOT / subdir
    directory.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4()}.{extension}"
    (directory / filename).write_bytes(data)
    return f"{subdir}/{filename}"


def read_bytes(key: str) -> bytes:
    return _full_path(key).read_bytes()


def delete(key: str) -> None:
    path = _full_path(key)
    if path.exists():
        path.unlink()
