import uuid

from sqlalchemy.orm import Session

from app.models.body_measurement import BodyMeasurement
from app.models.style_preference import StylePreference
from app.models.user_profile import UserProfile

# These three tables are all 1-to-1 with a user and all follow the same
# "may not exist yet" shape, so one small repository covers all of them
# instead of three near-identical files.


def get_profile(db: Session, user_id: uuid.UUID) -> UserProfile | None:
    return db.query(UserProfile).filter(UserProfile.user_id == user_id).first()


def upsert_profile(db: Session, user_id: uuid.UUID, fields: dict) -> UserProfile:
    profile = get_profile(db, user_id)
    if profile is None:
        profile = UserProfile(user_id=user_id)
        db.add(profile)
    for key, value in fields.items():
        setattr(profile, key, value)
    db.commit()
    db.refresh(profile)
    return profile


def get_measurements(db: Session, user_id: uuid.UUID) -> BodyMeasurement | None:
    return (
        db.query(BodyMeasurement).filter(BodyMeasurement.user_id == user_id).first()
    )


def upsert_measurements(
    db: Session, user_id: uuid.UUID, fields: dict
) -> BodyMeasurement:
    measurement = get_measurements(db, user_id)
    if measurement is None:
        measurement = BodyMeasurement(user_id=user_id)
        db.add(measurement)
    for key, value in fields.items():
        setattr(measurement, key, value)
    db.commit()
    db.refresh(measurement)
    return measurement


def get_style_preferences(db: Session, user_id: uuid.UUID) -> StylePreference | None:
    return (
        db.query(StylePreference).filter(StylePreference.user_id == user_id).first()
    )


def upsert_style_preferences(
    db: Session, user_id: uuid.UUID, fields: dict
) -> StylePreference:
    style = get_style_preferences(db, user_id)
    if style is None:
        style = StylePreference(user_id=user_id)
        db.add(style)
    for key, value in fields.items():
        setattr(style, key, value)
    db.commit()
    db.refresh(style)
    return style
