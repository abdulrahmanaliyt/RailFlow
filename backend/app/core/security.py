
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

import jwt

from datetime import datetime, timedelta, timezone
from typing import Any

from app.core.config import settings


# Password hashing configuration
password_hash = PasswordHash((Argon2Hasher(),))


def hash_password(password: str) -> str:
    """Hash a plain-text password using Argon2."""
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    """Verify a plain-text password against its hash."""
    return password_hash.verify(plain_password, hashed_password)


# JWT token generation
def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None
) -> str:

    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + (
        expires_delta
        or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


# JWT token verification
def decode_access_token(token: str) -> dict[str, Any]:

    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM]
    )

    return payload
