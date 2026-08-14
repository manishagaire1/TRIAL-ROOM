"""
Unit tests for the color-coordination rule engine. Mirrors the scenarios
manually verified against the live API in Phase 9.
"""

import uuid

from app.models.clothing import Clothing
from app.models.style_preference import StylePreference
from app.services.style_recommendation_service import get_suggestions


def _item(name, category, color, tags=None) -> Clothing:
    item = Clothing(name=name, category=category, primary_color=color, tags=tags or [])
    item.id = uuid.uuid4()
    return item


def test_neutral_anchor_matches_neutral_and_tagged_items():
    shirt = _item("Classic Oxford Shirt", "Shirt", "Navy", tags=["work"])
    chinos = _item("Classic Chinos", "Pants", "Beige", tags=["work", "casual"])
    jeans = _item("Straight-Fit Jeans", "Jeans", "Indigo", tags=["casual"])
    sneakers = _item("White Canvas Sneakers", "Shoes", "White", tags=["casual"])
    catalog = [shirt, chinos, jeans, sneakers]

    suggestions = get_suggestions(shirt, catalog, occasion="work", style_preference=None)

    names_by_slot = {s["slot"]: [] for s in suggestions}
    for s in suggestions:
        names_by_slot.setdefault(s["slot"], []).append(s["item"].name)

    assert "Classic Chinos" in names_by_slot["bottom"]
    assert "White Canvas Sneakers" in names_by_slot["shoes"]
    # Chinos is tagged for the requested occasion, so it should rank
    # ahead of the (also-compatible) jeans within the "bottom" slot.
    assert names_by_slot["bottom"][0] == "Classic Chinos"


def test_favorite_color_boosts_ranking():
    shirt = _item("Classic Oxford Shirt", "Shirt", "Navy", tags=["work"])
    chinos = _item("Classic Chinos", "Pants", "Beige", tags=["work"])
    jeans = _item("Straight-Fit Jeans", "Jeans", "Indigo", tags=["work"])
    catalog = [shirt, chinos, jeans]

    preference = StylePreference(favorite_colors=["Indigo"], styles=[])
    suggestions = get_suggestions(shirt, catalog, occasion="work", style_preference=preference)

    bottoms = [s["item"].name for s in suggestions if s["slot"] == "bottom"]
    assert bottoms[0] == "Straight-Fit Jeans"


def test_no_other_items_in_catalog_returns_no_suggestions():
    accessory = _item("Leather Belt", "Accessories", "Brown")
    suggestions = get_suggestions(accessory, [accessory], occasion=None, style_preference=None)
    assert suggestions == []
