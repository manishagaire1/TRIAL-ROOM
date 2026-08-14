"""
Unit tests for the size recommendation algorithm — pure Python objects,
no database, no HTTP. These mirror the exact scenarios manually verified
against the live API in Phase 8, now automated so a future change can't
silently break them.
"""

from app.models.clothing import Clothing
from app.models.size_chart import ClothingSize, SizeChart
from app.services.size_recommendation_service import recommend_size


def _tops_chart() -> SizeChart:
    chart = SizeChart(name="Standard Tops", category="tops")
    chart.sizes = [
        ClothingSize(size_label="S", chest_cm=88, waist_cm=70, hip_cm=90, length_cm=65),
        ClothingSize(size_label="M", chest_cm=94, waist_cm=76, hip_cm=96, length_cm=67),
        ClothingSize(size_label="L", chest_cm=100, waist_cm=82, hip_cm=102, length_cm=69),
        ClothingSize(size_label="XL", chest_cm=106, waist_cm=88, hip_cm=108, length_cm=71),
    ]
    return chart


def _jeans_chart() -> SizeChart:
    chart = SizeChart(name="Straight Jeans Fit", category="jeans")
    chart.sizes = [
        ClothingSize(size_label="28", waist_cm=71, hip_cm=94, length_cm=102),
        ClothingSize(size_label="30", waist_cm=76, hip_cm=99, length_cm=104),
        ClothingSize(size_label="32", waist_cm=81, hip_cm=104, length_cm=106),
        ClothingSize(size_label="34", waist_cm=86, hip_cm=109, length_cm=108),
        ClothingSize(size_label="36", waist_cm=91, hip_cm=114, length_cm=110),
    ]
    return chart


def _shirt(size_chart: SizeChart | None) -> Clothing:
    shirt = Clothing(name="Classic Oxford Shirt", category="Shirt", primary_color="Navy")
    shirt.size_chart = size_chart
    return shirt


def _jeans() -> Clothing:
    jeans = Clothing(name="Straight-Fit Jeans", category="Jeans", primary_color="Indigo")
    jeans.size_chart = _jeans_chart()
    return jeans


def test_recommends_closest_match_and_relaxed_alternative():
    result = recommend_size(
        _shirt(_tops_chart()),
        fit_preference="relaxed",
        measurements={"chest_cm": 97, "waist_cm": None, "hip_cm": None},
        usual_sizes={},
    )
    assert result.recommended_size == "M"
    assert result.alternative_size == "L"
    assert result.confidence == "high"


def test_recommends_smaller_size_when_closer():
    result = recommend_size(
        _shirt(_tops_chart()),
        fit_preference=None,
        measurements={"chest_cm": 90, "waist_cm": None, "hip_cm": None},
        usual_sizes={},
    )
    assert result.recommended_size == "S"


def test_bottoms_use_waist_and_hip():
    result = recommend_size(
        _jeans(),
        fit_preference=None,
        measurements={"chest_cm": None, "waist_cm": 82, "hip_cm": 105},
        usual_sizes={},
    )
    assert result.recommended_size == "32"


def test_falls_back_to_usual_size_when_no_measurements():
    result = recommend_size(
        _shirt(_tops_chart()),
        fit_preference="slim",
        measurements={"chest_cm": None, "waist_cm": None, "hip_cm": None},
        usual_sizes={"usual_shirt_size": "L", "usual_pants_size": None, "usual_dress_size": None},
    )
    assert result.recommended_size == "L"
    assert result.alternative_size == "M"  # slim -> a size down
    assert result.confidence == "low"


def test_honest_when_no_information_at_all():
    result = recommend_size(
        _shirt(_tops_chart()),
        fit_preference=None,
        measurements={"chest_cm": None, "waist_cm": None, "hip_cm": None},
        usual_sizes={},
    )
    assert result.recommended_size is None
    assert "profile" in result.explanation.lower()


def test_honest_when_product_has_no_size_chart():
    result = recommend_size(
        _shirt(None),
        fit_preference=None,
        measurements={"chest_cm": 94, "waist_cm": None, "hip_cm": None},
        usual_sizes={},
    )
    assert result.recommended_size is None
    assert "size chart" in result.explanation.lower()
