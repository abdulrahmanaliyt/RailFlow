
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


ScheduleStatus = Literal["SCHEDULED", "CANCELLED", "COMPLETED"]


class TrainScheduleCreate(BaseModel):
    route_id: int = Field(gt=0)
    journey_date: date
    scheduled_departure_at: datetime
    scheduled_arrival_at: datetime

    @model_validator(mode="after")
    def validate_schedule(self):
        departure = self.scheduled_departure_at
        arrival = self.scheduled_arrival_at

        if departure.tzinfo is None or departure.utcoffset() is None:
            raise ValueError("Departure must include a timezone offset.")

        if arrival.tzinfo is None or arrival.utcoffset() is None:
            raise ValueError("Arrival must include a timezone offset.")

        if arrival <= departure:
            raise ValueError("Arrival must be later than departure.")

        if self.journey_date != departure.date():
            raise ValueError(
                "Journey date must match the departure date."
            )

        return self


class TrainScheduleUpdate(BaseModel):
    journey_date: date
    scheduled_departure_at: datetime
    scheduled_arrival_at: datetime
    status: ScheduleStatus

    @model_validator(mode="after")
    def validate_schedule(self):
        departure = self.scheduled_departure_at
        arrival = self.scheduled_arrival_at

        if departure.tzinfo is None or departure.utcoffset() is None:
            raise ValueError("Departure must include a timezone offset.")

        if arrival.tzinfo is None or arrival.utcoffset() is None:
            raise ValueError("Arrival must include a timezone offset.")

        if arrival <= departure:
            raise ValueError("Arrival must be later than departure.")

        if self.journey_date != departure.date():
            raise ValueError(
                "Journey date must match the departure date."
            )

        return self


class TrainScheduleResponse(BaseModel):
    id: int
    route_id: int
    journey_date: date
    scheduled_departure_at: datetime
    scheduled_arrival_at: datetime
    status: ScheduleStatus

    model_config = ConfigDict(from_attributes=True)
