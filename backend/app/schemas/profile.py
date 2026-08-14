import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

FitPreference = Literal["slim", "regular", "relaxed", "oversized"]
BodyShape = Literal[
    "rectangle", "triangle", "inverted_triangle", "hourglass", "oval", "not_sure"
]
MeasurementSystem = Literal["metric", "imperial"]
ColorGroup = Literal["neutral", "dark", "light", "pastel", "bright"]


# --- Basic profile ---


class UserProfileUpdate(BaseModel):
    name: str | None = None
    age_range: str | None = None
    gender_preference: str | None = None
    country_region: str | None = None
    measurement_system: MeasurementSystem | None = None


class UserProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str | None = None
    age_range: str | None = None
    gender_preference: str | None = None
    country_region: str | None = None
    measurement_system: MeasurementSystem = "metric"
    updated_at: datetime | None = None


# --- Body measurements ---


class BodyMeasurementUpdate(BaseModel):
    height_cm: float | None = None
    weight_kg: float | None = None
    usual_shirt_size: str | None = None
    usual_pants_size: str | None = None
    usual_dress_size: str | None = None
    chest_cm: float | None = None
    waist_cm: float | None = None
    hip_cm: float | None = None
    shoulder_cm: float | None = None
    inseam_cm: float | None = None
    arm_length_cm: float | None = None
    leg_length_cm: float | None = None
    foot_size: float | None = None
    fit_preference: FitPreference | None = None
    body_shape: BodyShape | None = None


class BodyMeasurementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    height_cm: float | None = None
    weight_kg: float | None = None
    usual_shirt_size: str | None = None
    usual_pants_size: str | None = None
    usual_dress_size: str | None = None
    chest_cm: float | None = None
    waist_cm: float | None = None
    hip_cm: float | None = None
    shoulder_cm: float | None = None
    inseam_cm: float | None = None
    arm_length_cm: float | None = None
    leg_length_cm: float | None = None
    foot_size: float | None = None
    fit_preference: FitPreference | None = None
    body_shape: BodyShape | None = None
    ai_estimated: bool = False
    updated_at: datetime | None = None


# --- Style preferences ---


class StylePreferenceUpdate(BaseModel):
    favorite_colors: list[str] | None = None
    color_group: ColorGroup | None = None
    styles: list[str] | None = None
    occasions: list[str] | None = None


class StylePreferenceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    favorite_colors: list[str] = []
    color_group: ColorGroup | None = None
    styles: list[str] = []
    occasions: list[str] = []
    updated_at: datetime | None = None
