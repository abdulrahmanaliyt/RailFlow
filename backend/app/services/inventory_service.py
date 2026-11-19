from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.train import Train
from app.models.coach import Coach
from app.models.seat import Seat


class NotFoundError(Exception):
    pass


class ConflictError(Exception):
    pass


def create_coach(db: Session, train_id: int, data):
    train = db.get(Train, train_id)

    if not train:
        raise NotFoundError("Train not found.")

    coach = Coach(
        train_id=train_id,
        coach_number=data.coach_number.strip().upper(),
        coach_type=data.coach_type,
    )

    try:
        db.add(coach)
        db.commit()
        db.refresh(coach)
        return coach
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError(
            "A coach with this number already exists for this train."
        ) from exc


def get_train_coaches(db: Session, train_id: int):
    if not db.get(Train, train_id):
        raise NotFoundError("Train not found.")

    statement = (
        select(Coach)
        .where(Coach.train_id == train_id)
        .order_by(Coach.coach_number)
    )
    return db.scalars(statement).all()


def get_coach(db: Session, coach_id: int):
    coach = db.get(Coach, coach_id)

    if not coach:
        raise NotFoundError("Coach not found.")

    return coach


def update_coach(db: Session, coach_id: int, data):
    coach = get_coach(db, coach_id)

    coach.coach_number = data.coach_number.strip().upper()
    coach.coach_type = data.coach_type
    coach.is_active = data.is_active

    try:
        db.commit()
        db.refresh(coach)
        return coach
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError(
            "A coach with this number already exists for this train."
        ) from exc


def deactivate_coach(db: Session, coach_id: int):
    coach = get_coach(db, coach_id)

    coach.is_active = False
    db.commit()

    return coach


def create_seat(db: Session, coach_id: int, data):
    coach = db.get(Coach, coach_id)

    if not coach:
        raise NotFoundError("Coach not found.")

    if not coach.is_active:
        raise ConflictError("Cannot add a seat to an inactive coach.")

    seat = Seat(
        coach_id=coach_id,
        seat_number=data.seat_number.strip().upper(),
        berth_type=data.berth_type,
    )

    try:
        db.add(seat)
        db.commit()
        db.refresh(seat)
        return seat
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError(
            "A seat with this number already exists in this coach."
        ) from exc


def get_coach_seats(db: Session, coach_id: int):
    if not db.get(Coach, coach_id):
        raise NotFoundError("Coach not found.")

    statement = (
        select(Seat)
        .where(Seat.coach_id == coach_id)
        .order_by(Seat.seat_number)
    )
    return db.scalars(statement).all()


def get_seat(db: Session, seat_id: int):
    seat = db.get(Seat, seat_id)

    if not seat:
        raise NotFoundError("Seat not found.")

    return seat


def update_seat(db: Session, seat_id: int, data):
    seat = get_seat(db, seat_id)

    seat.seat_number = data.seat_number.strip().upper()
    seat.berth_type = data.berth_type
    seat.is_active = data.is_active

    try:
        db.commit()
        db.refresh(seat)
        return seat
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError(
            "A seat with this number already exists in this coach."
        ) from exc


def deactivate_seat(db: Session, seat_id: int):
    seat = get_seat(db, seat_id)

    seat.is_active = False
    db.commit()

    return seat