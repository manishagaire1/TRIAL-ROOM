import uuid

from sqlalchemy.orm import Session

from app.models.body_measurement import BodyMeasurement
from app.models.style_preference import StylePreference
from app.models.user_profile import UserProfile
from app.repositories import profile_repository
from app.schemas.profile import (
    BodyMeasurementUpdate,
    StylePreferenceUpdate,
    UserProfileUpdate,
)


def get_profile(db: Session, user_id: uuid.UUID) -> UserProfile | None:
    return profile_repository.get_profile(db, user_id)


def update_profile(
    db: Session, user_id: uuid.UUID, data: UserProfileUpdate
) -> UserProfile:
    # exclude_unset (not exclude_none): a field the client omits entirely
    # is left untouched, but a field explicitly sent as null overwrites
    # the stored value — this is what lets Quick Mode fill in a couple of
    # fields now and Accurate Mode add the rest later without wiping data.
    fields = data.model_dump(exclude_unset=True)
    return profile_repository.upsert_profile(db, user_id, fields)


def get_measurements(db: Session, user_id: uuid.UUID) -> BodyMeasurement | None:
    return profile_repository.get_measurements(db, user_id)


def update_measurements(
    db: Session, user_id: uuid.UUID, data: BodyMeasurementUpdate
) -> BodyMeasurement:
    fields = data.model_dump(exclude_unset=True)
    return profile_repository.upsert_measurements(db, user_id, fields)


def get_style_preferences(
    db: Session, user_id: uuid.UUID
) -> StylePreference | None:
    return profile_repository.get_style_preferences(db, user_id)


def update_style_preferences(
    db: Session, user_id: uuid.UUID, data: StylePreferenceUpdate
) -> StylePreference:
    fields = data.model_dump(exclude_unset=True)
    return profile_repository.upsert_style_preferences(db, user_id, fields)
