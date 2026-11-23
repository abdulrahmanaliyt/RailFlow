from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import RouteStop, TrainRoute, TrainSchedule


def route_exists(db: Session, route_id: int) -> bool:
    return db.get(TrainRoute, route_id) is not None


def create_schedule(db: Session, data):
    route = db.get(TrainRoute, data.route_id)

    if route is None:
        raise LookupError("Train route not found.")

    if not route.is_active:
        raise ValueError(
            "Cannot create a schedule for an inactive route."
        )

    stop_count = db.scalar(
        select(func.count())
        .select_from(RouteStop)
        .where(RouteStop.route_id == data.route_id)
    )

    if stop_count < 2:
        raise ValueError(
            "A route must contain at least two stops."
        )

    schedule = TrainSchedule(**data.model_dump())

    db.add(schedule)

    try:
        db.commit()
        db.refresh(schedule)
        return schedule
    except Exception:
        db.rollback()
        raise


def get_all_schedules(
    db: Session,
    status: str | None = None,
    route_id: int | None = None,
):
    statement = select(TrainSchedule).order_by(
        TrainSchedule.scheduled_departure_at
    )

    if status is not None:
        statement = statement.where(TrainSchedule.status == status)

    if route_id is not None:
        statement = statement.where(TrainSchedule.route_id == route_id)

    return db.scalars(statement).all()


def get_schedule_by_id(db: Session, schedule_id: int):
    return db.get(TrainSchedule, schedule_id)


def get_schedules_by_route(db: Session, route_id: int):
    statement = (
        select(TrainSchedule)
        .where(TrainSchedule.route_id == route_id)
        .order_by(TrainSchedule.scheduled_departure_at)
    )
    return db.scalars(statement).all()


def update_schedule(
    db: Session,
    schedule_id: int,
    data,
):
    schedule = db.get(TrainSchedule, schedule_id)

    if schedule is None:
        return None

    if schedule.status != "SCHEDULED":
        raise ValueError("Only scheduled journeys can be updated.")

    updates = data.model_dump(exclude_unset=True)

    if not updates:
        raise ValueError("No fields provided for update.")

    if "route_id" in updates:
        raise ValueError(
            "Cannot change route_id of an existing schedule."
        )

    for key, value in updates.items():
        if value is None:
            raise ValueError(f"{key} cannot be null.")

    for key, value in updates.items():
        setattr(schedule, key, value)

    if schedule.scheduled_departure_at >= schedule.scheduled_arrival_at:
        raise ValueError("Departure must be before arrival.")

    try:
        db.commit()
        db.refresh(schedule)
        return schedule
    except Exception:
        db.rollback()
        raise


def cancel_schedule(db: Session, schedule_id: int):
    schedule = db.get(TrainSchedule, schedule_id)

    if schedule is None:
        return None

    if schedule.status == "COMPLETED":
        raise ValueError("A completed schedule cannot be cancelled.")

    if schedule.status == "CANCELLED":
        raise ValueError("Schedule is already cancelled.")

    schedule.status = "CANCELLED"

    try:
        db.commit()
        db.refresh(schedule)
        return schedule
    except Exception:
        db.rollback()
        raise


def complete_schedule(db: Session, schedule_id: int):
    schedule = db.get(TrainSchedule, schedule_id)

    if schedule is None:
        return None

    if schedule.status == "CANCELLED":
        raise ValueError("A cancelled schedule cannot be completed.")

    if schedule.status == "COMPLETED":
        raise ValueError("Schedule is already completed.")

    schedule.status = "COMPLETED"

    try:
        db.commit()
        db.refresh(schedule)
        return schedule
    except Exception:
        db.rollback()
        raise