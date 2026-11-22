from pydantic import BaseModel, ConfigDict, Field
from typing import Literal


CoachType = Literal["1A", "2A", "3A", "SL", "CC", "2S"]
BerthType = Literal[
    "LOWER",
    "MIDDLE",
    "UPPER",
    "SIDE_LOWER",
    "SIDE_UPPER",
    "SEAT",
]


class CoachCreate(BaseModel):
    coach_number: str = Field(min_length=1, max_length=10)
    coach_type: CoachType


class CoachUpdate(BaseModel):
    coach_number: str = Field(min_length=1, max_length=10)
    coach_type: CoachType
    is_active: bool


class CoachResponse(BaseModel):
    id: int
    train_id: int
    coach_number: str
    coach_type: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class SeatCreate(BaseModel):
    seat_number: str = Field(min_length=1, max_length=10)
    berth_type: BerthType


class SeatBulkCreate(BaseModel):
    seats: list[SeatCreate] = Field(min_length=1)


class SeatUpdate(BaseModel):
    seat_number: str = Field(min_length=1, max_length=10)
    berth_type: BerthType
    is_active: bool


class SeatResponse(BaseModel):
    id: int
    coach_id: int
    seat_number: str
    berth_type: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)