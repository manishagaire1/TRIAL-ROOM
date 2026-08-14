"""
docs/11 (master spec Section 11) / docs/01: size recommendations are a
deterministic comparison against the product's real size chart — never
an AI/ML call, and never presented as guaranteed. This module is a pure
function over plain data so it's easy to unit test without a database.
"""

from app.models.clothing import Clothing
from app.models.size_chart import ClothingSize
from app.schemas.size_recommendation import SizeRecommendationResponse

_TOPS = {"T-shirt", "Shirt", "Hoodie", "Sweater", "Jacket", "Coat"}
_BOTTOMS = {"Jeans", "Pants", "Shorts", "Skirt"}


def _measurement_priority(category: str) -> list[str]:
    """Which chart columns matter for this category, most important
    first. Shoes/Accessories/Traditional clothing aren't chest-waist-hip
    garments, so they're intentionally unsupported for now — returning
    [] routes them to the honest "not enough info" response."""
    if category in _TOPS:
        return ["chest_cm", "waist_cm"]
    if category == "Dress":
        return ["chest_cm", "waist_cm", "hip_cm"]
    if category in _BOTTOMS:
        return ["waist_cm", "hip_cm"]
    return []


def _usual_size_field(category: str) -> str | None:
    if category in _TOPS:
        return "usual_shirt_size"
    if category in _BOTTOMS:
        return "usual_pants_size"
    if category == "Dress":
        return "usual_dress_size"
    return None


def _fit_label(diff_cm: float) -> str:
    """How the recommended size will feel, based on how much extra room
    its measurement gives beyond the user's actual measurement."""
    if diff_cm < 2:
        return "slim"
    if diff_cm < 6:
        return "regular"
    if diff_cm < 10:
        return "relaxed"
    return "oversized"


def _neighbor_index(sizes: list[ClothingSize], index: int, direction: str | None) -> int | None:
    """direction: 'up' for a looser alternative, 'down' for a tighter
    one. Falls back to whichever neighbor exists if the preferred one
    doesn't (e.g. already the largest size)."""
    up = index + 1 if index + 1 < len(sizes) else None
    down = index - 1 if index - 1 >= 0 else None
    if direction == "down":
        return down if down is not None else up
    return up if up is not None else down


def recommend_size(
    clothing: Clothing,
    fit_preference: str | None,
    measurements: dict[str, float | None],
    usual_sizes: dict[str, str | None],
) -> SizeRecommendationResponse:
    if not clothing.size_chart or not clothing.size_chart.sizes:
        return SizeRecommendationResponse(
            recommended_size=None,
            alternative_size=None,
            estimated_fit=None,
            confidence="low",
            explanation="This item doesn't have a size chart yet, so we can't estimate a size.",
        )

    sizes = clothing.size_chart.sizes  # already ordered by waist_cm ascending
    priority = _measurement_priority(clothing.category)
    relevant = {
        field: measurements[field]
        for field in priority
        if measurements.get(field) is not None
    }

    if relevant:
        return _recommend_from_measurements(sizes, priority, relevant, fit_preference)

    usual_field = _usual_size_field(clothing.category)
    usual_size = usual_sizes.get(usual_field) if usual_field else None
    return _recommend_from_usual_size(sizes, usual_size, fit_preference)


def _recommend_from_measurements(
    sizes: list[ClothingSize],
    priority: list[str],
    relevant: dict[str, float],
    fit_preference: str | None,
) -> SizeRecommendationResponse:
    weights = {field: (2 if i == 0 else 1) for i, field in enumerate(priority)}

    best_index, best_distance = None, None
    for i, size in enumerate(sizes):
        distance, compared_any = 0.0, False
        for field, user_value in relevant.items():
            chart_value = getattr(size, field)
            if chart_value is None:
                continue
            distance += weights[field] * (chart_value - user_value) ** 2
            compared_any = True
        if compared_any and (best_distance is None or distance < best_distance):
            best_index, best_distance = i, distance

    if best_index is None:
        return SizeRecommendationResponse(
            recommended_size=None,
            alternative_size=None,
            estimated_fit=None,
            confidence="low",
            explanation="This item's size chart doesn't have the measurements needed to compare against.",
        )

    recommended = sizes[best_index]
    primary_field = priority[0]
    primary_chart_value = getattr(recommended, primary_field)
    primary_user_value = relevant.get(primary_field)

    if primary_user_value is not None and primary_chart_value is not None:
        diff = primary_chart_value - primary_user_value
        estimated_fit = _fit_label(diff)
        confidence = "high"
    else:
        # Only a secondary field (e.g. waist for a top) was available.
        estimated_fit = "regular"
        confidence = "medium"

    direction = "up" if fit_preference in ("relaxed", "oversized") else (
        "down" if fit_preference == "slim" else None
    )
    alt_index = _neighbor_index(sizes, best_index, direction)
    alternative = sizes[alt_index].size_label if alt_index is not None else None

    field_summary = ", ".join(
        f"{field.replace('_cm', '')} {value:g}cm" for field, value in relevant.items()
    )
    explanation = (
        f"Based on your {field_summary} compared to this item's size chart, "
        f"{recommended.size_label} is the closest match."
    )
    if alternative and fit_preference in ("relaxed", "oversized"):
        explanation += f" For a more {fit_preference} feel, consider {alternative}."
    elif alternative and fit_preference == "slim":
        explanation += f" For a slimmer feel, consider {alternative}."

    return SizeRecommendationResponse(
        recommended_size=recommended.size_label,
        alternative_size=alternative,
        estimated_fit=estimated_fit,
        confidence=confidence,
        explanation=explanation,
    )


def _recommend_from_usual_size(
    sizes: list[ClothingSize], usual_size: str | None, fit_preference: str | None
) -> SizeRecommendationResponse:
    if not usual_size:
        return SizeRecommendationResponse(
            recommended_size=None,
            alternative_size=None,
            estimated_fit=None,
            confidence="low",
            explanation="Add your measurements or usual size in your profile to get a size recommendation.",
        )

    matches = [i for i, s in enumerate(sizes) if s.size_label == usual_size]
    if not matches:
        return SizeRecommendationResponse(
            recommended_size=None,
            alternative_size=None,
            estimated_fit=None,
            confidence="low",
            explanation=f"Your usual size ({usual_size}) isn't offered for this item.",
        )

    index = matches[0]
    direction = "up" if fit_preference in ("relaxed", "oversized") else (
        "down" if fit_preference == "slim" else None
    )
    alt_index = _neighbor_index(sizes, index, direction)
    alternative = sizes[alt_index].size_label if alt_index is not None else None

    return SizeRecommendationResponse(
        recommended_size=usual_size,
        alternative_size=alternative,
        estimated_fit=fit_preference or "regular",
        confidence="low",
        explanation=(
            f"We used your usual size ({usual_size}) since no measurements were "
            "available for this category."
        ),
    )
