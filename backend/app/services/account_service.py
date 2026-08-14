from sqlalchemy.orm import Session

from app.core import storage
from app.models.user import User
from app.repositories import photo_repository, tryon_repository, wardrobe_repository

_ALL = 10_000  # effectively "no pagination" for a single user's own rows


def delete_account(db: Session, user: User) -> None:
    """
    Section 25: account deletion must remove the DB rows AND the stored
    files. ON DELETE CASCADE handles every DB row transitively (profile,
    measurements, photos, jobs, outfits, wardrobe items — all FK to
    users.id), but cascade never touches the filesystem, so every
    storage key has to be collected and deleted explicitly — the same
    lesson learned the hard way with orphaned files in earlier phases.
    """
    storage_keys: list[str] = []

    photo = photo_repository.get_by_user(db, user.id)
    if photo:
        storage_keys.append(photo.storage_key)

    wardrobe_items, _ = wardrobe_repository.list_for_user(db, user.id, page=1, page_size=_ALL)
    storage_keys.extend(item.storage_key for item in wardrobe_items)

    jobs, _ = tryon_repository.list_jobs_for_user(db, user.id, page=1, page_size=_ALL)
    storage_keys.extend(job.result.storage_key for job in jobs if job.result)

    db.delete(user)
    db.commit()

    for key in storage_keys:
        storage.delete(key)
