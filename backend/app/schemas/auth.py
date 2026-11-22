
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# Registration request
class UserRegister(BaseModel):

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128
    )


# Login request
class UserLogin(BaseModel):

    email: EmailStr

    password: str


# User information returned by the API
class UserResponse(BaseModel):

    id: int
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# JWT response
class Token(BaseModel):

    access_token: str
    token_type: Literal["bearer"] = "bearer"


# Data extracted from JWT
class TokenData(BaseModel):

    sub: str | None = None
