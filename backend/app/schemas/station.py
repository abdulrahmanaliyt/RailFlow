from pydantic import BaseModel, ConfigDict, Field, field_validator
import re


class StationCreate(BaseModel):

    station_code: str = Field(
        min_length=2,
        max_length=10,
    )

    name: str = Field(
        min_length=2,
        max_length=150,
    )

    city: str = Field(
        min_length=2,
        max_length=100,
    )

    state: str = Field(
        min_length=2,
        max_length=100,
    )

    @field_validator("station_code")
    @classmethod
    def validate_station_code(cls, value):
        value = value.strip().upper()

        if not re.fullmatch(r"[A-Z0-9]{2,10}", value):
            raise ValueError(
                "Station code must contain only letters and numbers."
            )

        return value

    @field_validator("name", "city", "state")
    @classmethod
    def clean_text(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Field cannot be empty.")

        return value


class StationUpdate(BaseModel):

    station_code: str | None = Field(
        default=None,
        min_length=2,
        max_length=10,
    )

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    city: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    state: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    @field_validator("station_code")
    @classmethod
    def validate_station_code(cls, value):
        if value is None:
            return value

        value = value.strip().upper()

        if not re.fullmatch(r"[A-Z0-9]{2,10}", value):
            raise ValueError(
                "Station code must contain only letters and numbers."
            )

        return value

    @field_validator("name", "city", "state")
    @classmethod
    def clean_text(cls, value):
        if value is None:
            return value

        value = value.strip()

        if not value:
            raise ValueError("Field cannot be empty.")

        return value


class StationResponse(BaseModel):

    id: int
    station_code: str
    name: str
    city: str
    state: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)