import uuid
from typing import Literal

from pydantic import BaseModel

Confidence = Literal["low", "medium", "high"]


class SizeRecommendationRequest(BaseModel):
    clothing_id: uuid.UUID
    # Every field below is optional — if omitted, the service falls back
    # to the current user's saved BodyMeasurement/UserProfile values, so
    # a returning user gets a recommendation with zero extra typing while
    # a guest can still get one by passing everything explicitly.
    fit_preference: str | None = None
    height_cm: float | None = None
    weight_kg: float | None = None
    chest_cm: float | None = None
    waist_cm: float | None = None
    hip_cm: float | None = None
    usual_shirt_size: str | None = None
    usual_pants_size: str | None = None
    usual_dress_size: str | None = None


class SizeRecommendationResponse(BaseModel):
    recommended_size: str | None
    alternative_size: str | None
    estimated_fit: str | None
    confidence: Confidence
    explanation: str
