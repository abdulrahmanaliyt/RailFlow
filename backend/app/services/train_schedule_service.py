from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import RouteStop, TrainRoute, TrainSchedule


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
    db.commit()
    db.refresh(schedule)

    return schedule


def get_all_schedules(db: Session):
    statement = select(TrainSchedule).order_by(
        TrainSchedule.scheduled_departure_at
    )
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

    updates = data.model_dump(exclude_unset=True)

    # Validate target route if route_id is being updated
    if "route_id" in updates and updates["route_id"] is not None:
        target_route = db.get(TrainRoute, updates["route_id"])

        if target_route is None:
            raise LookupError("Train route not found.")

        if not target_route.is_active:
            raise ValueError(
                "Cannot assign a schedule to an inactive route."
            )

        stop_count = db.scalar(
            select(func.count())
            .select_from(RouteStop)
            .where(RouteStop.route_id == updates["route_id"])
        )

        if stop_count < 2:
            raise ValueError(
                "A route must contain at least two stops."
            )

    for key, value in updates.items():
        setattr(schedule, key, value)

    db.commit()
    db.refresh(schedule)

    return schedule


def route_exists(db: Session, route_id: int) -> bool:
    return db.get(TrainRoute, route_id) is not None