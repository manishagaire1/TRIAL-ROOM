import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, model_validator


class OutfitItemInput(BaseModel):
    """One slot's pick in the Outfit Builder — exactly one of
    clothing_id/wardrobe_item_id, matching the OutfitItem check
    constraint. `slot` is optional; the service infers it from the
    item's category when omitted."""

    clothing_id: uuid.UUID | None = None
    wardrobe_item_id: uuid.UUID | None = None
    slot: str | None = None

    @model_validator(mode="after")
    def _exactly_one_source(self):
        if (self.clothing_id is None) == (self.wardrobe_item_id is None):
            raise ValueError("Provide exactly one of clothing_id or wardrobe_item_id.")
        return self


class SavedOutfitCreate(BaseModel):
    name: str | None = None
    occasion: str | None = None
    # Legacy single-item convenience (Phase 10's "save this try-on as an
    # outfit") — still supported alongside the multi-item builder below.
    clothing_id: uuid.UUID | None = None
    # Phase 11 Outfit Builder: one entry per slot (top/bottom/shoes/...).
    items: list[OutfitItemInput] | None = None

    @model_validator(mode="after")
    def _has_at_least_one_item(self):
        if self.clothing_id is None and not self.items:
            raise ValueError("Provide either clothing_id or items.")
        return self


class SavedOutfitUpdate(BaseModel):
    liked: bool | None = None
    name: str | None = None
    occasion: str | None = None


class OutfitItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    clothing_id: uuid.UUID | None
    wardrobe_item_id: uuid.UUID | None
    source: str
    name: str
    category: str
    primary_color: str
    slot: str


class SavedOutfitRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str | None
    occasion: str | None
    liked: bool
    created_at: datetime
    items: list[OutfitItemRead]


class PaginatedOutfits(BaseModel):
    items: list[SavedOutfitRead]
    total: int
    page: int
    page_size: int


class CompareRequest(BaseModel):
    outfit_ids: list[uuid.UUID]
    occasion: str | None = None


class OutfitComparisonEntry(BaseModel):
    outfit: SavedOutfitRead
    explanation: str
    is_strongest_match: bool


class CompareResponse(BaseModel):
    entries: list[OutfitComparisonEntry]
    summary: str
