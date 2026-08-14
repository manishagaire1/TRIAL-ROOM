from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings

JWT_ALGORITHM = "HS256"


def hash_password(plain_password: str) -> str:
    """Hash a password for storage. Never store plain-text passwords."""
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), password_hash.encode("utf-8")
    )


def create_access_token(user_id: str) -> str:
    """
    Build a JWT whose `sub` (subject) claim is the user's id. Any route
    that needs to know who's calling decodes this token instead of
    trusting anything the client sends directly.
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_expiry_minutes
    )
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Raises jwt.PyJWTError (expired, malformed, bad signature, etc.)."""
    return jwt.decode(token, settings.jwt_secret, algorithms=[JWT_ALGORITHM])
