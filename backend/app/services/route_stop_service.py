from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    RouteSegment,
    RouteStop,
    Station,
    TrainRoute,
    TrainSchedule,
)


def route_exists(db: Session, route_id: int) -> bool:
    return db.get(TrainRoute, route_id) is not None


def get_active_route(db: Session, route_id: int):
    statement = select(TrainRoute).where(
        TrainRoute.id == route_id,
        TrainRoute.is_active.is_(True),
    )

    return db.scalar(statement)


def get_route_stop_by_id(db: Session, stop_id: int):
    return db.get(RouteStop, stop_id)


def get_all_route_stops(db: Session):
    statement = (
        select(RouteStop)
        .order_by(
            RouteStop.route_id,
            RouteStop.stop_sequence,
        )
    )

    return db.scalars(statement).all()


def get_stops_by_route(db: Session, route_id: int):
    statement = (
        select(RouteStop)
        .where(RouteStop.route_id == route_id)
        .order_by(RouteStop.stop_sequence)
    )

    return db.scalars(statement).all()


def route_is_operational(db: Session, route_id: int) -> bool:
    segment_statement = select(RouteSegment.id).where(
        RouteSegment.route_id == route_id
    ).limit(1)

    schedule_statement = select(TrainSchedule.id).where(
        TrainSchedule.route_id == route_id
    ).limit(1)

    has_segments = db.scalar(segment_statement) is not None
    has_schedules = db.scalar(schedule_statement) is not None

    return has_segments or has_schedules


def validate_route_and_station(
    db: Session,
    route_id: int,
    station_id: int,
):
    route = db.get(TrainRoute, route_id)

    if route is None:
        raise LookupError("Train route not found.")

    if not route.is_active:
        raise ValueError("Cannot modify stops of an inactive route.")

    station = db.get(Station, station_id)

    if station is None:
        raise LookupError("Station not found.")

    if not station.is_active:
        raise ValueError("Cannot add an inactive station to a route.")


def create_route_stop(db: Session, data):
    validate_route_and_station(
        db,
        data.route_id,
        data.station_id,
    )

    if route_is_operational(db, data.route_id):
        raise ValueError(
            "Route stops cannot be modified after schedules or "
            "route segments have been created."
        )

    route_stop = RouteStop(
        route_id=data.route_id,
        station_id=data.station_id,
        stop_sequence=data.stop_sequence,
    )

    db.add(route_stop)

    try:
        db.commit()
        db.refresh(route_stop)

        return route_stop

    except Exception:
        db.rollback()
        raise

def update_route_stop(db: Session, stop_id: int, data):
    route_stop = db.get(RouteStop, stop_id)

    if route_stop is None:
        return None

    if route_is_operational(db, route_stop.route_id):
        raise ValueError(
            "Route stops cannot be modified after schedules or "
            "route segments have been created."
        )

    validate_route_and_station(
        db,
        route_stop.route_id,
        route_stop.station_id,
    )

    update_data = data.model_dump(exclude_unset=True)

    if not update_data:
        raise ValueError("Provide at least one field to update.")

    for field, value in update_data.items():
        if value is None:
            raise ValueError(f"{field} cannot be null.")

    if "station_id" in update_data:
        validate_route_and_station(
            db,
            route_stop.route_id,
            update_data["station_id"],
        )

    for field, value in update_data.items():
        setattr(route_stop, field, value)

    try:
        db.commit()
        db.refresh(route_stop)

        return route_stop

    except Exception:
        db.rollback()
        raise
    
    
def delete_route_stop(db: Session, stop_id: int):
    route_stop = db.get(RouteStop, stop_id)

    if route_stop is None:
        return False

    if route_is_operational(db, route_stop.route_id):
        raise ValueError(
            "Route stops cannot be deleted after schedules or "
            "route segments have been created."
        )

    try:
        db.delete(route_stop)
        db.commit()

        return True

    except Exception:
        db.rollback()
        raise