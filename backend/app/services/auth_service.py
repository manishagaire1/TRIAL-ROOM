import secrets
import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import EmailAlreadyRegisteredError, InvalidCredentialsError
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories import user_repository
from app.schemas.auth import UserCreate, UserLogin


def register_user(db: Session, data: UserCreate) -> User:
    if user_repository.get_by_email(db, data.email):
        raise EmailAlreadyRegisteredError()
    return user_repository.create_user(db, data.email, hash_password(data.password))


def authenticate_user(db: Session, data: UserLogin) -> User:
    user = user_repository.get_by_email(db, data.email)
    if not user or not verify_password(data.password, user.password_hash):
        raise InvalidCredentialsError()
    return user


def issue_token_for(user: User) -> str:
    return create_access_token(str(user.id))


def create_guest_user(db: Session) -> User:
    """
    Section 24: guests can use the core experience (try-on, size
    recommendation) without registering, but their actions still need a
    real user_id to attach to in the database. This creates a normal
    User row (is_guest=True) with an unguessable placeholder email and a
    random, never-shared password — there is no login flow for guest
    accounts, only the token issued right here.
    """
    # ".local" is an IANA-reserved special-use TLD and gets rejected by
    # EmailStr validation on the way back out in API responses — use an
    # ordinary-looking (never-emailed) domain instead.
    placeholder_email = f"guest-{uuid.uuid4()}@guest.virtualfitai.com"
    unusable_password_hash = hash_password(secrets.token_urlsafe(32))
    return user_repository.create_user(
        db, placeholder_email, unusable_password_hash, is_guest=True
    )
