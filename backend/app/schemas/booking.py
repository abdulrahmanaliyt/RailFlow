from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict


# Passenger information submitted by the client
class PassengerCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    age: int = Field(ge=0, le=120)
    gender: str = Field(pattern="^(M|F|OTHER)$")


# One passenger and their selected seat
class BookingPassengerCreate(PassengerCreate):
    seat_id: int = Field(gt=0)


# Complete booking request
class BookingCreate(BaseModel):
    schedule_id: int = Field(gt=0)

    origin_station_code: str = Field(
        min_length=2,
        max_length=10
    )

    destination_station_code: str = Field(
        min_length=2,
        max_length=10
    )

    passengers: list[BookingPassengerCreate] = Field(
        min_length=1,
        max_length=6
    )


# Passenger information returned to the client
class PassengerResponse(BaseModel):
    id: int
    full_name: str
    age: int
    gender: str

    model_config = ConfigDict(from_attributes=True)


# Seat allocation information
class SeatReservationResponse(BaseModel):
    seat_id: int
    seat_number: str
    coach_number: str
    coach_type: str
    berth_type: str
    reservation_status: str


# Passenger with assigned seat
class BookedPassengerResponse(BaseModel):
    passenger: PassengerResponse
    seat: SeatReservationResponse


# Booking response
class BookingResponse(BaseModel):
    id: int
    pnr: str
    user_id: int
    schedule_id: int

    origin_station_code: str
    destination_station_code: str

    status: str
    total_amount: Decimal
    created_at: datetime

    passengers: list[BookedPassengerResponse]