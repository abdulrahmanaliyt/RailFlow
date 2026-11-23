from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class TrainSearchResult(BaseModel):
    schedule_id: int

    train_id: int
    train_number: str
    train_name: str

    route_id: int

    from_station_code: str
    from_station_name: str
    from_sequence: int

    to_station_code: str
    to_station_name: str
    to_sequence: int

    journey_date: date

    scheduled_departure_at: datetime
    scheduled_arrival_at: datetime

    status: str

    model_config = ConfigDict(from_attributes=True)