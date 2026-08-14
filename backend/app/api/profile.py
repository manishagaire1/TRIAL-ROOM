from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.profile import (
    BodyMeasurementRead,
    BodyMeasurementUpdate,
    StylePreferenceRead,
    StylePreferenceUpdate,
)
from app.services import profile_service

router = APIRouter(tags=["profile"])


@router.get("/body-measurements", response_model=BodyMeasurementRead)
def read_measurements(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    measurements = profile_service.get_measurements(db, current_user.id)
    return measurements if measurements else BodyMeasurementRead()


@router.put("/body-measurements", response_model=BodyMeasurementRead)
@router.post("/body-measurements", response_model=BodyMeasurementRead)
def update_measurements(
    data: BodyMeasurementUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return profile_service.update_measurements(db, current_user.id, data)


@router.get("/style-preferences", response_model=StylePreferenceRead)
def read_style_preferences(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    style = profile_service.get_style_preferences(db, current_user.id)
    return style if style else StylePreferenceRead()


@router.put("/style-preferences", response_model=StylePreferenceRead)
def update_style_preferences(
    data: StylePreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return profile_service.update_style_preferences(db, current_user.id, data)
