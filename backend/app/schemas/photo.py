from datetime import datetime

from pydantic import BaseModel


class UserPhotoRead(BaseModel):
    has_photo: bool
    updated_at: datetime | None = None
