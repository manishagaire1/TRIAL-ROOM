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
