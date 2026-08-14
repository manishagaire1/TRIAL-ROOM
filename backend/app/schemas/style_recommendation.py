import uuid

from pydantic import BaseModel


class StyleRecommendationRequest(BaseModel):
    clothing_id: uuid.UUID
    occasion: str | None = None


class StyleSuggestion(BaseModel):
    clothing_id: uuid.UUID
    name: str
    category: str
    primary_color: str
    price: float
    currency: str
    slot: str
    reason: str


class StyleRecommendationResponse(BaseModel):
    anchor_clothing_id: uuid.UUID
    anchor_name: str
    anchor_color: str
    occasion: str | None
    suggestions: list[StyleSuggestion]
    note: str
