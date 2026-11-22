
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.models.user import User
from app.core.security import hash_password, verify_password


def register_user(
    db: Session,
    email: str,
    password: str
) -> User:

    normalized_email = email.strip().lower()

    existing_user = db.scalar(
        select(User).where(
            func.lower(User.email) == normalized_email
        )
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered"
        )

    new_user = User(
        email=normalized_email,
        password_hash=hash_password(password),
        role="passenger",
        is_active=True
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

    except IntegrityError:
        db.rollback()

        existing_user = db.scalar(
            select(User).where(
                func.lower(User.email) == normalized_email
            )
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email is already registered"
            )

        raise

    return new_user


def authenticate_user(
    db: Session,
    email: str,
    password: str
) -> User | None:

    normalized_email = email.strip().lower()

    user = db.scalar(
        select(User).where(
            func.lower(User.email) == normalized_email
        )
    )

    if user is None:
        return None

    if not verify_password(password, user.password_hash):
        return None

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is inactive"
        )

    return user
