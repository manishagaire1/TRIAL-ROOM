import uuid

from sqlalchemy.orm import Session

from app.core import storage
from app.models.user import User
from app.models.user_photo import UserPhoto
from app.repositories import photo_repository
from app.utils.image_validation import validate_and_normalize_image


def upload_photo(db: Session, user: User, raw_bytes: bytes) -> UserPhoto:
    normalized = validate_and_normalize_image(raw_bytes)

    existing = photo_repository.get_by_user(db, user.id)
    new_key = storage.save_bytes("photos", "jpg", normalized)
    photo = photo_repository.upsert(db, user.id, new_key)

    # Only remove the old file after the new one is safely saved and the
    # DB row committed — never delete-then-write.
    if existing and existing.storage_key != new_key:
        storage.delete(existing.storage_key)

    return photo


def delete_photo(db: Session, user: User) -> None:
    deleted = photo_repository.delete(db, user.id)
    if deleted:
        storage.delete(deleted.storage_key)


def get_photo(db: Session, user_id: uuid.UUID) -> UserPhoto | None:
    return photo_repository.get_by_user(db, user_id)


def get_photo_bytes(db: Session, user_id: uuid.UUID) -> bytes | None:
    photo = photo_repository.get_by_user(db, user_id)
    if photo is None:
        return None
    return storage.read_bytes(photo.storage_key)
