"""
docs/01 Section 5C / master spec Section 15: outfit suggestions come from
general color-coordination conventions and the user's own stated
preferences — never from anything about the user's body or appearance.
Rule-based on purpose (docs/02-user-flows.md): a real ML recommender is a
future upgrade behind this same function signature, not the MVP.
"""

import uuid

from app.models.clothing import Clothing
from app.models.style_preference import StylePreference

NOTE = (
    "These suggestions are based on general color-coordination "
    "conventions and your stated preferences — not a claim about what "
    "looks best on you."
)

_NEUTRALS = {"black", "white", "gray", "navy", "beige", "brown", "charcoal"}

# Non-neutral colors that conventionally pair well together, beyond the
# "neutrals go with everything" rule below. Deliberately small and
# editorial rather than exhaustive — easy to extend.
_COMPLEMENTARY_PAIRS: dict[str, set[str]] = {
    "red": {"navy", "denim", "indigo"},
    "pink": {"navy"},
    "purple": set(),
    "green": {"beige", "brown"},
    "olive": {"beige", "brown"},
    "blue": {"beige", "brown"},
    "light blue": {"beige", "brown"},
    "indigo": {"olive", "red"},
}

_CATEGORY_SLOT = {
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

_TARGET_SLOTS = {
    "top": ["bottom", "shoes"],
    "outerwear": ["bottom", "shoes"],
    "bottom": ["top", "shoes"],
    "dress": ["shoes", "accessory"],
    "shoes": ["top", "bottom"],
    "accessory": ["top", "bottom"],
}

SUGGESTIONS_PER_SLOT = 2


def _colors_pair(anchor_color: str, candidate_color: str) -> tuple[bool, str]:
    anchor, candidate = anchor_color.lower(), candidate_color.lower()
    if candidate in _NEUTRALS:
        return True, f"{candidate_color} is a neutral that pairs easily with {anchor_color}."
    if anchor in _NEUTRALS:
        return True, f"{anchor_color} is neutral, so it pairs well with {candidate_color}."
    if candidate in _COMPLEMENTARY_PAIRS.get(anchor, set()):
        return True, f"{candidate_color} is a classic pairing with {anchor_color}."
    return False, ""


def get_suggestions(
    anchor: Clothing,
    catalog: list[Clothing],
    occasion: str | None,
    style_preference: StylePreference | None,
) -> list[dict]:
    anchor_slot = _CATEGORY_SLOT.get(anchor.category)
    if anchor_slot is None:
        return []

    favorite_colors = {c.lower() for c in (style_preference.favorite_colors if style_preference else [])}
    preferred_styles = {s.lower() for s in (style_preference.styles if style_preference else [])}

    scored: dict[str, list[tuple[float, dict]]] = {slot: [] for slot in _TARGET_SLOTS[anchor_slot]}

    for item in catalog:
        if item.id == anchor.id:
            continue
        slot = _CATEGORY_SLOT.get(item.category)
        if slot not in scored:
            continue

        does_pair, reason = _colors_pair(anchor.primary_color, item.primary_color)
        if not does_pair:
            continue

        score = 1.0
        if occasion and occasion.lower() in [t.lower() for t in item.tags]:
            reason += f" Also tagged for {occasion}."
            score += 1
        if item.primary_color.lower() in favorite_colors:
            reason += " It's also one of your favorite colors."
            score += 1
        if preferred_styles and preferred_styles.intersection(t.lower() for t in item.tags):
            score += 0.5

        scored[slot].append((score, {"item": item, "reason": reason}))

    suggestions: list[dict] = []
    for slot, candidates in scored.items():
        candidates.sort(key=lambda pair: pair[0], reverse=True)
        for _, entry in candidates[:SUGGESTIONS_PER_SLOT]:
            suggestions.append({"slot": slot, **entry})

    return suggestions
