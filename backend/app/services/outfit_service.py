import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ValidationError
from app.models.outfit import SavedOutfit
from app.models.style_preference import StylePreference
from app.models.user import User
from app.repositories import (
    clothing_repository,
    outfit_repository,
    profile_repository,
    wardrobe_repository,
)
from app.repositories.outfit_repository import OutfitItemSpec
from app.schemas.outfit import (
    CompareRequest,
    CompareResponse,
    OutfitComparisonEntry,
    OutfitItemInput,
    PaginatedOutfits,
    SavedOutfitCreate,
    SavedOutfitUpdate,
)
from app.services.slot_mapping import slot_for_category

# Master spec Section 17: never claim objective knowledge of which
# outfit "looks best" — every comparison sentence stays preference-based.
_NO_SIGNAL_SUMMARY = (
    "Add style preferences in your profile, or an occasion when comparing, "
    "to get a personalized comparison."
)
_TIE_SUMMARY = "These outfits are similarly matched based on your preferences."


def _resolve_item(db: Session, user: User, item_input: OutfitItemInput) -> tuple[OutfitItemSpec, str]:
    """Validates one Outfit Builder slot pick and returns the spec to
    persist plus a display name (for defaulting the outfit's name)."""
    if item_input.clothing_id is not None:
        clothing = clothing_repository.get_by_id(db, item_input.clothing_id)
        if clothing is None:
            raise NotFoundError("One of the selected clothing items no longer exists.")
        slot = item_input.slot or slot_for_category(clothing.category)
        return OutfitItemSpec(slot=slot, clothing_id=clothing.id), clothing.name

    wardrobe_item = wardrobe_repository.get_by_id(db, item_input.wardrobe_item_id)
    if wardrobe_item is None or wardrobe_item.user_id != user.id:
        raise NotFoundError("One of the selected wardrobe items was not found.")
    slot = item_input.slot or slot_for_category(wardrobe_item.category)
    return OutfitItemSpec(slot=slot, wardrobe_item_id=wardrobe_item.id), (
        wardrobe_item.label or wardrobe_item.category
    )


def create_outfit(db: Session, user: User, data: SavedOutfitCreate) -> SavedOutfit:
    if data.items:
        specs_and_names = [_resolve_item(db, user, item) for item in data.items]
    else:
        # Legacy single-item path (Phase 10: "save this try-on as an outfit").
        clothing = clothing_repository.get_by_id(db, data.clothing_id)
        if clothing is None:
            raise NotFoundError("This clothing item no longer exists.")
        specs_and_names = [
            (OutfitItemSpec(slot=slot_for_category(clothing.category), clothing_id=clothing.id), clothing.name)
        ]

    specs = [s for s, _name in specs_and_names]
    # Default to the item name(s) so an unnamed outfit still reads as
    # something specific ("Navy Shirt + Beige Chinos") instead of a
    # generic placeholder in lists and comparison summaries.
    default_name = " + ".join(name for _s, name in specs_and_names)
    name = data.name or default_name
    return outfit_repository.create_outfit(db, user.id, specs, name, data.occasion)


def list_outfits(db: Session, user: User, page: int, page_size: int) -> PaginatedOutfits:
    outfits, total = outfit_repository.list_for_user(db, user.id, page, page_size)
    return PaginatedOutfits(items=outfits, total=total, page=page, page_size=page_size)


def _get_owned(db: Session, user: User, outfit_id: uuid.UUID) -> SavedOutfit:
    outfit = outfit_repository.get_by_id(db, outfit_id)
    if outfit is None or outfit.user_id != user.id:
        raise NotFoundError("Outfit not found.")
    return outfit


def update_outfit(
    db: Session, user: User, outfit_id: uuid.UUID, data: SavedOutfitUpdate
) -> SavedOutfit:
    outfit = _get_owned(db, user, outfit_id)
    fields = data.model_dump(exclude_unset=True)
    return outfit_repository.update(db, outfit, fields)


def delete_outfit(db: Session, user: User, outfit_id: uuid.UUID) -> None:
    outfit = _get_owned(db, user, outfit_id)
    outfit_repository.delete(db, outfit)


def _score_outfit(
    outfit: SavedOutfit,
    occasion: str | None,
    favorite_colors: set[str],
    preferred_styles: set[str],
) -> tuple[float, list[str]]:
    score = 0.0
    notes: list[str] = []
    for outfit_item in outfit.items:
        # Wardrobe items don't carry catalog tags, so occasion/style
        # matching only applies to catalog-sourced items — favorite
        # color matching works for both via the shared property.
        tags_lower = [t.lower() for t in outfit_item.clothing.tags] if outfit_item.clothing else []
        if occasion and occasion.lower() in tags_lower:
            score += 2
            notes.append(f"{outfit_item.name} is tagged for {occasion}.")
        if outfit_item.primary_color.lower() in favorite_colors:
            score += 1
            notes.append(f"{outfit_item.name}'s color is one of your favorites.")
        if preferred_styles and preferred_styles.intersection(tags_lower):
            score += 0.5
    return score, notes


def compare_outfits(db: Session, user: User, data: CompareRequest) -> CompareResponse:
    if len(data.outfit_ids) < 2:
        raise ValidationError("Select at least 2 outfits to compare.")

    outfits = outfit_repository.get_many_for_user(db, data.outfit_ids, user.id)
    if len(outfits) != len(set(data.outfit_ids)):
        raise NotFoundError("One or more outfits were not found.")
    # Preserve the order the client asked to compare in.
    outfits.sort(key=lambda o: data.outfit_ids.index(o.id))

    style_pref: StylePreference | None = profile_repository.get_style_preferences(db, user.id)
    favorite_colors = {c.lower() for c in (style_pref.favorite_colors if style_pref else [])}
    preferred_styles = {s.lower() for s in (style_pref.styles if style_pref else [])}

    scored = [
        (_score_outfit(o, data.occasion, favorite_colors, preferred_styles), o) for o in outfits
    ]
    max_score = max(score for (score, _notes), _o in scored)
    has_signal = max_score > 0
    winners = [o for (score, _notes), o in scored if score == max_score] if has_signal else []
    is_tie = len(winners) > 1

    entries = []
    for (score, notes), outfit in scored:
        is_winner = has_signal and not is_tie and outfit.id == winners[0].id
        if notes:
            explanation = " ".join(notes)
        else:
            explanation = "No strong color or occasion match found for this outfit."
        entries.append(
            OutfitComparisonEntry(outfit=outfit, explanation=explanation, is_strongest_match=is_winner)
        )

    if not has_signal:
        summary = _NO_SIGNAL_SUMMARY
    elif is_tie:
        summary = _TIE_SUMMARY
    else:
        winner_name = winners[0].name or "This outfit"
        occasion_phrase = f" for a {data.occasion} occasion" if data.occasion else ""
        summary = (
            f"Based on your selected style preferences, {winner_name} may be a "
            f"stronger match{occasion_phrase}."
        )

    return CompareResponse(entries=entries, summary=summary)
