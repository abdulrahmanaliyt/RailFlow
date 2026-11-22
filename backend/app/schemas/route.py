import re

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RouteCreate(BaseModel):
    train_id: int = Field(gt=0)
    route_name: str = Field(min_length=2, max_length=150)

    @field_validator("route_name")
    @classmethod
    def validate_route_name(cls, value: str) -> str:
        value = value.strip()

        if len(value) < 2:
            raise ValueError("Route name must contain at least 2 characters.")

        return value


class RouteUpdate(BaseModel):
    route_name: str | None = Field(default=None, min_length=2, max_length=150)

    @field_validator("route_name")
    @classmethod
    def validate_route_name(cls, value: str | None) -> str | None:
        if value is None:
            return value

        value = value.strip()

        if len(value) < 2:
            raise ValueError("Route name must contain at least 2 characters.")

        return value


class RouteResponse(BaseModel):
    id: int
    train_id: int
    route_name: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)