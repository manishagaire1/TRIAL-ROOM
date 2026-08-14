import uuid

from sqlalchemy.orm import Session

from app.models.user_photo import UserPhoto


def get_by_user(db: Session, user_id: uuid.UUID) -> UserPhoto | None:
    return db.query(UserPhoto).filter(UserPhoto.user_id == user_id).first()


def get_by_id(db: Session, photo_id: uuid.UUID) -> UserPhoto | None:
    return db.query(UserPhoto).filter(UserPhoto.id == photo_id).first()


def upsert(db: Session, user_id: uuid.UUID, storage_key: str) -> UserPhoto:
    photo = get_by_user(db, user_id)
    if photo is None:
        photo = UserPhoto(user_id=user_id, storage_key=storage_key)
        db.add(photo)
    else:
        photo.storage_key = storage_key
    db.commit()
    db.refresh(photo)
    return photo


def delete(db: Session, user_id: uuid.UUID) -> UserPhoto | None:
    photo = get_by_user(db, user_id)
    if photo is None:
        return None
    db.delete(photo)
    db.commit()
    return photo
