import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class WardrobeItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    category: str
    color: str
    label: str | None
    created_at: datetime
    image_url: str


class PaginatedWardrobe(BaseModel):
    items: list[WardrobeItemRead]
    total: int
    page: int
    page_size: int
