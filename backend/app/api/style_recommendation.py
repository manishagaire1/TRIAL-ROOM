from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.repositories import clothing_repository, profile_repository
from app.schemas.style_recommendation import (
    StyleRecommendationRequest,
    StyleRecommendationResponse,
    StyleSuggestion,
)
from app.services import style_recommendation_service

router = APIRouter(prefix="/style-recommendation", tags=["style-recommendation"])


@router.post("", response_model=StyleRecommendationResponse)
def get_style_recommendation(
    data: StyleRecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    anchor = clothing_repository.get_by_id(db, data.clothing_id)
    if anchor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")

    catalog = clothing_repository.list_all(db)
    style_preference = profile_repository.get_style_preferences(db, current_user.id)

    raw_suggestions = style_recommendation_service.get_suggestions(
        anchor, catalog, data.occasion, style_preference
    )
    suggestions = [
        StyleSuggestion(
            clothing_id=entry["item"].id,
            name=entry["item"].name,
            category=entry["item"].category,
            primary_color=entry["item"].primary_color,
            price=entry["item"].price,
            currency=entry["item"].currency,
            slot=entry["slot"],
            reason=entry["reason"],
        )
        for entry in raw_suggestions
    ]

    return StyleRecommendationResponse(
        anchor_clothing_id=anchor.id,
        anchor_name=anchor.name,
        anchor_color=anchor.primary_color,
        occasion=data.occasion,
        suggestions=suggestions,
        note=style_recommendation_service.NOTE,
    )
