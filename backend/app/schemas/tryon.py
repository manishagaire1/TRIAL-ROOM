import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel

JobStatus = Literal["pending", "processing", "completed", "failed"]


class TryOnJobCreate(BaseModel):
    clothing_id: uuid.UUID
    selected_size: str
    selected_color: str


class TryOnResultRead(BaseModel):
    image_url: str
    provider: str
    created_at: datetime


class TryOnJobRead(BaseModel):
    id: uuid.UUID
    status: JobStatus
    clothing_id: uuid.UUID
    clothing_name: str
    selected_size: str
    selected_color: str
    failure_reason: str | None
    created_at: datetime
    completed_at: datetime | None
    result: TryOnResultRead | None = None


class PaginatedTryOnHistory(BaseModel):
    items: list[TryOnJobRead]
    total: int
    page: int
    page_size: int
