from collections.abc import Generator

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.database import SessionLocal
from app.models.user import User
from app.schemas.auth import TokenData

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# OAuth2 token extraction
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


# Get the currently authenticated user
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = decode_access_token(token)

        token_data = TokenData(
            sub=payload.get("sub")
        )

        user_id = token_data.sub

        if not user_id or not user_id.isdigit():
            raise credentials_exception

        user = db.get(User, int(user_id))

    except jwt.InvalidTokenError:
        raise credentials_exception

    if user is None or not user.is_active:
        raise credentials_exception

    return user


# Admin-only authorization
def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    role_value = getattr(current_user.role, "value", current_user.role)

    if str(role_value).upper() != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    return current_user