from datetime import datetime, timedelta, timezone
from secrets import choice
from string import ascii_uppercase, digits

from sqlalchemy import select, update
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.booking import Booking
from app.models.booking_passenger import BookingPassenger
from app.models.seat_segment_reservation import SeatSegmentReservation

from app.models.train_schedule import TrainSchedule
from app.models.train_route import TrainRoute
from app.models.train import Train

from app.models.route_stop import RouteStop
from app.models.route_segment import RouteSegment

from app.models.station import Station
from app.models.coach import Coach
from app.models.seat import Seat

from app.models.user import User


ACTIVE_STATUSES = ("HELD", "CONFIRMED")

HOLD_DURATION_MINUTES = 10

PNR_CHARACTERS = ascii_uppercase + digits


class BookingNotFoundError(Exception):
    pass


class BookingValidationError(Exception):
    pass


class BookingConflictError(Exception):
    pass


# Generate a unique PNR
def generate_pnr(db: Session) -> str:
    for _ in range(10):
        pnr = "".join(
            choice(PNR_CHARACTERS)
            for _ in range(10)
        )

        existing = db.scalar(
            select(Booking.id).where(
                Booking.pnr == pnr
            )
        )

        if existing is None:
            return pnr

    raise BookingConflictError(
        "Unable to generate a unique PNR. Please retry."
    )


# Validate schedule, route, and train availability
def get_valid_schedule(
    db: Session,
    schedule_id: int
):
    schedule = db.get(
        TrainSchedule,
        schedule_id
    )

    if schedule is None:
        raise BookingNotFoundError(
            "Train schedule not found."
        )

    if schedule.status != "SCHEDULED":
        raise BookingConflictError(
            "This train schedule is not available for booking."
        )

    route = db.get(
        TrainRoute,
        schedule.route_id
    )

    if route is None:
        raise BookingConflictError(
            "The route associated with this schedule no longer exists."
        )

    train = db.get(
        Train,
        route.train_id
    )

    if train is None or not train.is_active:
        raise BookingConflictError(
            "This train is currently inactive."
        )

    return schedule, route, train


# Validate active origin and destination stations and route stop order
def get_valid_journey(
    db: Session,
    route_id: int,
    origin_code: str,
    destination_code: str
):
    origin_code = origin_code.strip().upper()
    destination_code = destination_code.strip().upper()

    if origin_code == destination_code:
        raise BookingValidationError(
            "Origin and destination cannot be the same."
        )

    # Only active stations can be used for new bookings
    origin_station = db.scalar(
        select(Station).where(
            Station.station_code == origin_code,
            Station.is_active.is_(True),
        )
    )

    destination_station = db.scalar(
        select(Station).where(
            Station.station_code == destination_code,
            Station.is_active.is_(True),
        )
    )

    if origin_station is None:
        raise BookingNotFoundError(
            f"Active origin station '{origin_code}' not found."
        )

    if destination_station is None:
        raise BookingNotFoundError(
            f"Active destination station '{destination_code}' not found."
        )

    origin_stop = db.scalar(
        select(RouteStop).where(
            RouteStop.route_id == route_id,
            RouteStop.station_id == origin_station.id
        )
    )

    destination_stop = db.scalar(
        select(RouteStop).where(
            RouteStop.route_id == route_id,
            RouteStop.station_id == destination_station.id
        )
    )

    if origin_stop is None:
        raise BookingValidationError(
            "Origin station is not part of this train route."
        )

    if destination_stop is None:
        raise BookingValidationError(
            "Destination station is not part of this train route."
        )

    if (
        origin_stop.stop_sequence
        >= destination_stop.stop_sequence
    ):
        raise BookingValidationError(
            "Destination must be after origin."
        )

    return (
        origin_station,
        destination_station,
        origin_stop,
        destination_stop
    )


# Get and validate required route segments between origin and destination
def get_required_segments(
    db: Session,
    route_id: int,
    origin_stop: RouteStop,
    destination_stop: RouteStop
):
    route_stops = db.scalars(
        select(RouteStop)
        .where(RouteStop.route_id == route_id)
        .order_by(RouteStop.stop_sequence)
    ).all()

    expected_pairs = [
        (
            route_stops[index].id,
            route_stops[index + 1].id
        )
        for index in range(len(route_stops) - 1)
    ]

    route_segments = db.scalars(
        select(RouteSegment)
        .where(RouteSegment.route_id == route_id)
        .order_by(RouteSegment.segment_sequence)
    ).all()

    actual_pairs = [
        (
            segment.from_route_stop_id,
            segment.to_route_stop_id
        )
        for segment in route_segments
    ]

    if actual_pairs != expected_pairs:
        raise BookingConflictError(
            "Route segments are missing or inconsistent. "
            "Repair the route segments before booking."
        )

    stop_ids = [
        stop.id
        for stop in route_stops
    ]

    origin_index = stop_ids.index(
        origin_stop.id
    )

    destination_index = stop_ids.index(
        destination_stop.id
    )

    required_segments = route_segments[
        origin_index:destination_index
    ]

    if not required_segments:
        raise BookingValidationError(
            "No segments found for this journey."
        )

    return required_segments


# Expire old holds within this transaction
def expire_old_holds(
    db: Session,
    schedule_id: int
):
    db.execute(
        update(SeatSegmentReservation)
        .where(
            SeatSegmentReservation.schedule_id
            == schedule_id,

            SeatSegmentReservation.status
            == "HELD",

            SeatSegmentReservation.expires_at
            <= datetime.now(timezone.utc)
        )
        .values(
            status="EXPIRED"
        )
    )


# Validate and lock selected seats in sorted order to reduce deadlock risk
def validate_and_lock_seats(
    db: Session,
    train_id: int,
    seat_ids: list[int]
):
    sorted_seat_ids = sorted(seat_ids)

    statement = (
        select(Seat, Coach)
        .join(
            Coach,
            Seat.coach_id == Coach.id
        )
        .where(
            Seat.id.in_(sorted_seat_ids),
            Coach.train_id == train_id,
            Coach.is_active.is_(True),
            Seat.is_active.is_(True)
        )
        .order_by(Seat.id)
        .with_for_update(of=Seat)
    )

    rows = db.execute(statement).all()

    if len(rows) != len(sorted_seat_ids):
        raise BookingValidationError(
            "One or more selected seats are invalid, "
            "inactive, or do not belong to this train."
        )

    return {
        seat.id: (seat, coach)
        for seat, coach in rows
    }


# Check for active seat reservations across required segments
def check_seat_conflicts(
    db: Session,
    schedule_id: int,
    seat_ids: list[int],
    segment_ids: list[int]
):
    conflicts = db.scalars(
        select(SeatSegmentReservation)
        .where(
            SeatSegmentReservation.schedule_id
            == schedule_id,

            SeatSegmentReservation.seat_id
            .in_(seat_ids),

            SeatSegmentReservation.route_segment_id
            .in_(segment_ids),

            SeatSegmentReservation.status
            .in_(ACTIVE_STATUSES)
        )
    ).all()

    if conflicts:
        raise BookingConflictError(
            "One or more selected seats are no longer "
            "available for your complete journey. "
            "Please select different seats."
        )


# Create a booking, passengers, and held segment reservations in one transaction
def create_booking(
    db: Session,
    current_user: User,
    booking_data
):
    seat_ids = [
        passenger.seat_id
        for passenger in booking_data.passengers
    ]

    # Each passenger must receive a distinct seat
    if len(seat_ids) != len(set(seat_ids)):
        raise BookingValidationError(
            "Each passenger must have a different seat."
        )

    try:
        # Validate schedule, route, and train
        schedule, route, train = get_valid_schedule(
            db,
            booking_data.schedule_id
        )

        # Validate active origin and destination stations and stops
        (
            origin_station,
            destination_station,
            origin_stop,
            destination_stop
        ) = get_valid_journey(
            db,
            route.id,
            booking_data.origin_station_code,
            booking_data.destination_station_code
        )

        # Determine required route segments
        required_segments = get_required_segments(
            db,
            route.id,
            origin_stop,
            destination_stop
        )

        segment_ids = [
            segment.id
            for segment in required_segments
        ]

        # Expire stale holds inside this transaction
        expire_old_holds(
            db,
            schedule.id
        )

        # Lock selected seats
        locked_seats = validate_and_lock_seats(
            db,
            train.id,
            seat_ids
        )

        # Verify no active conflicts on any required segment
        check_seat_conflicts(
            db,
            schedule.id,
            seat_ids,
            segment_ids
        )

        # Generate PNR and create booking record
        pnr = generate_pnr(db)

        booking = Booking(
            pnr=pnr,
            user_id=current_user.id,
            schedule_id=schedule.id,
            from_route_stop_id=origin_stop.id,
            to_route_stop_id=destination_stop.id,
            status="PENDING_PAYMENT",
            total_amount=0
        )

        db.add(booking)

        # Flush so booking.id is available for child rows
        db.flush()

        # Create passenger records and held reservations per segment
        booked_passengers = []

        expires_at = (
            datetime.now(timezone.utc)
            + timedelta(
                minutes=HOLD_DURATION_MINUTES
            )
        )

        for passenger_data in booking_data.passengers:
            passenger = BookingPassenger(
                booking_id=booking.id,
                full_name=passenger_data.full_name.strip(),
                age=passenger_data.age,
                gender=passenger_data.gender
            )

            db.add(passenger)

            db.flush()

            seat, coach = locked_seats[
                passenger_data.seat_id
            ]

            for segment in required_segments:
                reservation = SeatSegmentReservation(
                    booking_id=booking.id,
                    passenger_id=passenger.id,
                    schedule_id=schedule.id,
                    seat_id=seat.id,
                    route_segment_id=segment.id,
                    status="HELD",
                    expires_at=expires_at
                )

                db.add(reservation)

            booked_passengers.append(
                {
                    "passenger": passenger,
                    "seat": seat,
                    "coach": coach
                }
            )

        db.commit()
        db.refresh(booking)

        return build_booking_response(
            booking=booking,
            origin_station=origin_station,
            destination_station=destination_station,
            booked_passengers=booked_passengers
        )

    except IntegrityError:
        db.rollback()
        raise BookingConflictError(
            "A seat was reserved by another request "
            "or a database constraint was violated. "
            "Please check availability and retry."
        )

    except Exception:
        db.rollback()
        raise


# Format booking response payload
def build_booking_response(
    booking,
    origin_station,
    destination_station,
    booked_passengers
):
    passengers_response = []

    for item in booked_passengers:
        passenger = item["passenger"]
        seat = item["seat"]
        coach = item["coach"]

        passengers_response.append(
            {
                "passenger": passenger,
                "seat": {
                    "seat_id": seat.id,
                    "seat_number": seat.seat_number,
                    "coach_number": coach.coach_number,
                    "coach_type": coach.coach_type,
                    "berth_type": seat.berth_type,
                    "reservation_status": "HELD"
                }
            }
        )

    return {
        "id": booking.id,
        "pnr": booking.pnr,
        "user_id": booking.user_id,
        "schedule_id": booking.schedule_id,
        "origin_station_code": origin_station.station_code,
        "destination_station_code": destination_station.station_code,
        "status": booking.status,
        "total_amount": booking.total_amount,
        "created_at": booking.created_at,
        "passengers": passengers_response
    }


# Retrieve a booking owned by current_user
def get_booking_by_id(
    db: Session,
    booking_id: int,
    current_user: User
):
    booking = db.scalar(
        select(Booking).where(
            Booking.id == booking_id,
            Booking.user_id == current_user.id
        )
    )

    if booking is None:
        raise BookingNotFoundError(
            "Booking not found."
        )

    passengers = db.scalars(
        select(BookingPassenger)
        .where(
            BookingPassenger.booking_id
            == booking.id
        )
        .order_by(BookingPassenger.id)
    ).all()

    reservations = db.scalars(
        select(SeatSegmentReservation)
        .where(
            SeatSegmentReservation.booking_id
            == booking.id
        )
    ).all()

    origin_stop = db.get(
        RouteStop,
        booking.from_route_stop_id
    )

    destination_stop = db.get(
        RouteStop,
        booking.to_route_stop_id
    )

    origin_station = db.get(
        Station,
        origin_stop.station_id
    )

    destination_station = db.get(
        Station,
        destination_stop.station_id
    )

    # Map each passenger to a single seat across multi-segment reservations
    passenger_seat_map = {}

    for reservation in reservations:
        if reservation.passenger_id not in passenger_seat_map:
            passenger_seat_map[
                reservation.passenger_id
            ] = reservation.seat_id

    passengers_response = []

    for passenger in passengers:
        seat_id = passenger_seat_map.get(
            passenger.id
        )

        seat = db.get(
            Seat,
            seat_id
        )

        coach = db.get(
            Coach,
            seat.coach_id
        )

        passenger_reservations = [
            reservation
            for reservation in reservations
            if reservation.passenger_id
            == passenger.id
        ]

        reservation_status = (
            passenger_reservations[0].status
            if passenger_reservations
            else "UNKNOWN"
        )

        passengers_response.append(
            {
                "passenger": passenger,
                "seat": {
                    "seat_id": seat.id,
                    "seat_number": seat.seat_number,
                    "coach_number": coach.coach_number,
                    "coach_type": coach.coach_type,
                    "berth_type": seat.berth_type,
                    "reservation_status": reservation_status
                }
            }
        )

    return {
        "id": booking.id,
        "pnr": booking.pnr,
        "user_id": booking.user_id,
        "schedule_id": booking.schedule_id,
        "origin_station_code": origin_station.station_code,
        "destination_station_code": destination_station.station_code,
        "status": booking.status,
        "total_amount": booking.total_amount,
        "created_at": booking.created_at,
        "passengers": passengers_response
    }


# Get current user's booking history
def get_my_bookings(
    db: Session,
    current_user: User
):
    bookings = db.scalars(
        select(Booking)
        .where(
            Booking.user_id == current_user.id
        )
        .order_by(
            Booking.created_at.desc()
        )
    ).all()

    return [
        get_booking_by_id(
            db,
            booking.id,
            current_user
        )
        for booking in bookings
    ]