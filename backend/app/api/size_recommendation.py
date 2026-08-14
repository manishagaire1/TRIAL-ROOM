from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.repositories import clothing_repository, profile_repository
from app.schemas.size_recommendation import (
    SizeRecommendationRequest,
    SizeRecommendationResponse,
)
from app.services.size_recommendation_service import recommend_size

router = APIRouter(prefix="/size-recommendation", tags=["size-recommendation"])


def _first_not_none(*values):
    for value in values:
        if value is not None:
            return value
    return None


@router.post("", response_model=SizeRecommendationResponse)
def get_size_recommendation(
    data: SizeRecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    clothing = clothing_repository.get_by_id(db, data.clothing_id)
    if clothing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")

    # Any field the request doesn't provide falls back to the user's
    # saved BodyMeasurement — so a returning user gets a useful result
    # with zero extra typing, while a guest can still get one by passing
    # everything explicitly in the request body.
    saved = profile_repository.get_measurements(db, current_user.id)

    measurements = {
        "chest_cm": _first_not_none(data.chest_cm, saved.chest_cm if saved else None),
        "waist_cm": _first_not_none(data.waist_cm, saved.waist_cm if saved else None),
        "hip_cm": _first_not_none(data.hip_cm, saved.hip_cm if saved else None),
    }
    usual_sizes = {
        "usual_shirt_size": _first_not_none(
            data.usual_shirt_size, saved.usual_shirt_size if saved else None
        ),
        "usual_pants_size": _first_not_none(
            data.usual_pants_size, saved.usual_pants_size if saved else None
        ),
        "usual_dress_size": _first_not_none(
            data.usual_dress_size, saved.usual_dress_size if saved else None
        ),
    }
    fit_preference = _first_not_none(
        data.fit_preference, saved.fit_preference if saved else None
    )

    return recommend_size(clothing, fit_preference, measurements, usual_sizes)
