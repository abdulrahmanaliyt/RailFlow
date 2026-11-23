from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

ScheduleStatus = Literal["SCHEDULED", "CANCELLED", "COMPLETED"]


class _ScheduleDateTimeMixin(BaseModel):
    @staticmethod
    def _validate_window(
        journey_date: date,
        departure: datetime,
        arrival: datetime,
    ) -> None:
        if departure.tzinfo is None or departure.utcoffset() is None:
            raise ValueError("Departure must include a timezone offset.")

        if arrival.tzinfo is None or arrival.utcoffset() is None:
            raise ValueError("Arrival must include a timezone offset.")

        if arrival <= departure:
            raise ValueError("Arrival must be later than departure.")

        if journey_date != departure.date():
            raise ValueError("Journey date must match the departure date.")


class TrainScheduleCreate(_ScheduleDateTimeMixin):
    route_id: int = Field(gt=0)
    journey_date: date
    scheduled_departure_at: datetime
    scheduled_arrival_at: datetime

    @model_validator(mode="after")
    def validate_schedule(self):
        self._validate_window(
            self.journey_date,
            self.scheduled_departure_at,
            self.scheduled_arrival_at,
        )
        return self


class TrainScheduleUpdate(_ScheduleDateTimeMixin):
    journey_date: date | None = None
    scheduled_departure_at: datetime | None = None
    scheduled_arrival_at: datetime | None = None
    status: ScheduleStatus | None = None

    @model_validator(mode="after")
    def validate_schedule(self):
        departure = self.scheduled_departure_at
        arrival = self.scheduled_arrival_at

        if departure is not None and (
            departure.tzinfo is None or departure.utcoffset() is None
        ):
            raise ValueError("Departure must include a timezone offset.")

        if arrival is not None and (
            arrival.tzinfo is None or arrival.utcoffset() is None
        ):
            raise ValueError("Arrival must include a timezone offset.")

        if departure is not None and arrival is not None and arrival <= departure:
            raise ValueError("Arrival must be later than departure.")

        if (
            self.journey_date is not None
            and departure is not None
            and self.journey_date != departure.date()
        ):
            raise ValueError("Journey date must match the departure date.")

        return self


class TrainScheduleResponse(BaseModel):
    id: int
    route_id: int
    journey_date: date
    scheduled_departure_at: datetime
    scheduled_arrival_at: datetime
    status: ScheduleStatus

    model_config = ConfigDict(from_attributes=True)


# Backwards-compatible aliases for routers/services importing unprefixed names
ScheduleCreate = TrainScheduleCreate
ScheduleUpdate = TrainScheduleUpdate
ScheduleResponse = TrainScheduleResponse