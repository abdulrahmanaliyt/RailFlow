from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.booking import Booking
from app.models.coach import Coach
from app.models.route_segment import RouteSegment
from app.models.route_stop import RouteStop
from app.models.seat import Seat
from app.models.seat_segment_reservation import SeatSegmentReservation
from app.models.station import Station
from app.models.train import Train
from app.models.train_route import TrainRoute
from app.models.train_schedule import TrainSchedule

ACTIVE_RESERVATION_STATUSES = ("HELD", "CONFIRMED")

ALLOWED_COACH_TYPES = {
    "1A",
    "2A",
    "3A",
    "SL",
    "CC",
    "2S",
}


class NotFoundError(Exception):
    pass


class ValidationError(Exception):
    pass


class ConflictError(Exception):
    pass


def get_schedule(db: Session, schedule_id: int):
    schedule = db.get(TrainSchedule, schedule_id)

    if not schedule:
        raise NotFoundError("Train schedule not found.")

    if schedule.status != "SCHEDULED":
        raise ConflictError(
            f"Seat availability cannot be checked for a "
            f"{schedule.status.lower()} schedule."
        )

    return schedule


def get_station(db: Session, station_code: str):
    normalized_code = station_code.strip().upper()

    station = db.scalar(
        select(Station).where(Station.station_code == normalized_code)
    )

    if not station:
        raise NotFoundError(
            f"Station '{normalized_code}' does not exist."
        )

    return station


def get_journey_stops(
    db: Session,
    route_id: int,
    origin_station_id: int,
    destination_station_id: int,
):
    origin_stop = db.scalar(
        select(RouteStop).where(
            RouteStop.route_id == route_id,
            RouteStop.station_id == origin_station_id,
        )
    )

    destination_stop = db.scalar(
        select(RouteStop).where(
            RouteStop.route_id == route_id,
            RouteStop.station_id == destination_station_id,
        )
    )

    if not origin_stop:
        raise ValidationError(
            "Origin station is not part of this train route."
        )

    if not destination_stop:
        raise ValidationError(
            "Destination station is not part of this train route."
        )

    if origin_stop.stop_sequence >= destination_stop.stop_sequence:
        raise ValidationError(
            "Destination must occur after origin on the route."
        )

    return origin_stop, destination_stop


def get_required_segments(
    db: Session,
    route_id: int,
    origin_stop: RouteStop,
    destination_stop: RouteStop,
):
    stops = db.scalars(
        select(RouteStop)
        .where(RouteStop.route_id == route_id)
        .order_by(RouteStop.stop_sequence)
    ).all()

    expected_pairs = [
        (stops[index].id, stops[index + 1].id)
        for index in range(len(stops) - 1)
    ]

    segments = db.scalars(
        select(RouteSegment)
        .where(RouteSegment.route_id == route_id)
        .order_by(RouteSegment.segment_sequence)
    ).all()

    actual_pairs = [
        (segment.from_route_stop_id, segment.to_route_stop_id)
        for segment in segments
    ]

    if actual_pairs != expected_pairs:
        raise ConflictError(
            "Route segments are missing or inconsistent with the "
            "current route stops. Regenerate or repair the route "
            "segments before checking seat availability."
        )

    stop_ids = [stop.id for stop in stops]

    origin_index = stop_ids.index(origin_stop.id)
    destination_index = stop_ids.index(destination_stop.id)

    required_segment_ids = [
        segment.id
        for segment in segments[origin_index:destination_index]
    ]

    if not required_segment_ids:
        raise ValidationError(
            "No route segments were found for this journey."
        )

    return required_segment_ids


def expire_booking_holds(db: Session, schedule_id: int | None = None) -> int:
    """
    Expire HELD seat reservations whose expires_at timestamp has passed,
    and cancel PENDING_PAYMENT bookings that no longer have any active HELD holds.

    Does NOT commit by itself so callers control transaction boundaries.
    """
    now = datetime.now(timezone.utc)

    hold_stmt = (
        update(SeatSegmentReservation)
        .where(
            SeatSegmentReservation.status == "HELD",
            SeatSegmentReservation.expires_at.is_not(None),
            SeatSegmentReservation.expires_at <= now,
        )
        .values(
            status="EXPIRED",
            expires_at=None,
        )
    )

    if schedule_id is not None:
        hold_stmt = hold_stmt.where(
            SeatSegmentReservation.schedule_id == schedule_id
        )

    result = db.execute(hold_stmt)

    bookings_with_active_holds = select(
        SeatSegmentReservation.booking_id
    ).where(
        SeatSegmentReservation.booking_id.is_not(None),
        SeatSegmentReservation.status == "HELD",
        SeatSegmentReservation.expires_at.is_not(None),
        SeatSegmentReservation.expires_at > now,
    )

    booking_stmt = (
        update(Booking)
        .where(
            Booking.status == "PENDING_PAYMENT",
            ~Booking.id.in_(bookings_with_active_holds),
        )
        .values(status="CANCELLED")
    )

    if schedule_id is not None:
        booking_stmt = booking_stmt.where(
            Booking.schedule_id == schedule_id
        )

    db.execute(booking_stmt)

    return result.rowcount

expire_old_holds = expire_booking_holds


def get_available_seats(
    db: Session,
    schedule_id: int,
    origin_code: str,
    destination_code: str,
    coach_type: str | None = None,
):
    origin_code = origin_code.strip().upper()
    destination_code = destination_code.strip().upper()

    if origin_code == destination_code:
        raise ValidationError(
            "Origin and destination stations cannot be the same."
        )

    if coach_type:
        coach_type = coach_type.strip().upper()

        if coach_type not in ALLOWED_COACH_TYPES:
            raise ValidationError(
                "Invalid coach type. Allowed values: "
                + ", ".join(sorted(ALLOWED_COACH_TYPES))
            )

    schedule = get_schedule(db, schedule_id)

    origin_station = get_station(db, origin_code)
    destination_station = get_station(db, destination_code)

    route = db.get(TrainRoute, schedule.route_id)

    if not route:
        raise ConflictError(
            "The schedule references a route that no longer exists."
        )

    train = db.get(Train, route.train_id)

    if not train or not train.is_active:
        raise ConflictError(
            "The train assigned to this schedule is inactive."
        )

    origin_stop, destination_stop = get_journey_stops(
        db=db,
        route_id=route.id,
        origin_station_id=origin_station.id,
        destination_station_id=destination_station.id,
    )

    required_segment_ids = get_required_segments(
        db=db,
        route_id=route.id,
        origin_stop=origin_stop,
        destination_stop=destination_stop,
    )

    try:
        expire_booking_holds(db, schedule.id)
        db.commit()
    except Exception:
        db.rollback()
        raise

    active_reservation_exists = (
        select(SeatSegmentReservation.id)
        .where(
            SeatSegmentReservation.schedule_id == schedule.id,
            SeatSegmentReservation.seat_id == Seat.id,
            SeatSegmentReservation.route_segment_id.in_(
                required_segment_ids
            ),
            SeatSegmentReservation.status.in_(
                ACTIVE_RESERVATION_STATUSES
            ),
        )
        .exists()
    )

    statement = (
        select(Seat, Coach)
        .join(Coach, Seat.coach_id == Coach.id)
        .where(
            Coach.train_id == train.id,
            Coach.is_active.is_(True),
            Seat.is_active.is_(True),
            ~active_reservation_exists,
        )
        .order_by(
            Coach.coach_number,
            Seat.seat_number,
        )
    )

    if coach_type:
        statement = statement.where(Coach.coach_type == coach_type)

    rows = db.execute(statement).all()

    available_seats = [
        {
            "seat_id": seat.id,
            "seat_number": seat.seat_number,
            "berth_type": seat.berth_type,
            "coach_id": coach.id,
            "coach_number": coach.coach_number,
            "coach_type": coach.coach_type,
        }
        for seat, coach in rows
    ]

    return {
        "schedule_id": schedule.id,
        "train_id": train.id,
        "train_number": train.train_number,
        "train_name": train.train_name,
        "route_id": route.id,
        "origin_station_code": origin_station.station_code,
        "origin_station_name": origin_station.name,
        "destination_station_code": destination_station.station_code,
        "destination_station_name": destination_station.name,
        "segments_required": len(required_segment_ids),
        "available_seat_count": len(available_seats),
        "available_seats": available_seats,
    }