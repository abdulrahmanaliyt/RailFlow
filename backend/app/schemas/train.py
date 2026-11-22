import re

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TrainCreate(BaseModel):
    train_number: str = Field(min_length=1, max_length=10)
    train_name: str = Field(min_length=2, max_length=150)

    @field_validator("train_number")
    @classmethod
    def validate_train_number(cls, value: str) -> str:
        value = value.strip().upper()

        if not re.fullmatch(r"[A-Z0-9]{1,10}", value):
            raise ValueError(
                "Train number must contain only letters and numbers."
            )

        return value

    @field_validator("train_name")
    @classmethod
    def validate_train_name(cls, value: str) -> str:
        value = value.strip()

        if len(value) < 2:
            raise ValueError("Train name must contain at least 2 characters.")

        return value


class TrainUpdate(BaseModel):
    train_number: str | None = Field(default=None, min_length=1, max_length=10)
    train_name: str | None = Field(default=None, min_length=2, max_length=150)

    @field_validator("train_number")
    @classmethod
    def validate_train_number(cls, value: str | None) -> str | None:
        if value is None:
            return value

        value = value.strip().upper()

        if not re.fullmatch(r"[A-Z0-9]{1,10}", value):
            raise ValueError(
                "Train number must contain only letters and numbers."
            )

        return value

    @field_validator("train_name")
    @classmethod
    def validate_train_name(cls, value: str | None) -> str | None:
        if value is None:
            return value

        value = value.strip()

        if len(value) < 2:
            raise ValueError("Train name must contain at least 2 characters.")

        return value


class TrainResponse(BaseModel):
    id: int
    train_number: str
    train_name: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)