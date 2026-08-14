"""
Which "slot" of an outfit a clothing category fills. Shared by the style
recommendation engine (Phase 9) and the outfit service (Phase 10) so the
two features can't silently drift apart on what counts as a "top" vs a
"bottom".
"""

CATEGORY_SLOT = {
    "T-shirt": "top",
    "Shirt": "top",
    "Hoodie": "top",
    "Sweater": "top",
    "Jacket": "outerwear",
    "Coat": "outerwear",
    "Dress": "dress",
    "Jeans": "bottom",
    "Pants": "bottom",
    "Shorts": "bottom",
    "Skirt": "bottom",
    "Shoes": "shoes",
    "Accessories": "accessory",
    "Traditional clothing": "top",
}


def slot_for_category(category: str) -> str:
    return CATEGORY_SLOT.get(category, "item")
