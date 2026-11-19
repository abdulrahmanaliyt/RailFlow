
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class TrainSearchResponse(BaseModel):
    schedule_id: int

    train_id: int
    train_number: str
    train_name: str

    route_id: int
    route_name: str

    origin_station_code: str
    origin_station_name: str
    origin_sequence: int

    destination_station_code: str
    destination_station_name: str
    destination_sequence: int

    journey_date: date
    scheduled_departure_at: datetime
    scheduled_arrival_at: datetime

    status: str

    model_config = ConfigDict(from_attributes=True)


class TrainSearchPageResponse(BaseModel):
    items: list[TrainSearchResponse]
    total: int
    limit: int
    offset: int
