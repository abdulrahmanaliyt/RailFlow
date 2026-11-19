from pydantic import BaseModel, ConfigDict


class AvailableSeatResponse(BaseModel):
    seat_id: int
    seat_number: str
    berth_type: str
    coach_id: int
    coach_number: str
    coach_type: str

    model_config = ConfigDict(from_attributes=True)


class SeatAvailabilityResponse(BaseModel):
    schedule_id: int
    train_id: int
    train_number: str
    train_name: str
    route_id: int

    origin_station_code: str
    origin_station_name: str
    destination_station_code: str
    destination_station_name: str

    segments_required: int
    available_seat_count: int
    available_seats: list[AvailableSeatResponse]