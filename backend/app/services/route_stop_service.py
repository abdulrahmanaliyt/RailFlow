from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import RouteStop

def create_route_stop(db: Session, data):
    route_stop = RouteStop(**data.model_dump())

    db.add(route_stop)
    db.commit()
    db.refresh(route_stop)

    return route_stop

def get_all_route_stops(db: Session):
    statement = select(RouteStop).order_by(
        RouteStop.route_id,
        RouteStop.stop_sequence
    )

    return db.scalars(statement).all()

def get_route_stop_by_id(db: Session, stop_id: int):
    return db.get(RouteStop, stop_id)

def get_stops_by_route(db: Session, route_id: int):
    statement = (
        select(RouteStop)
        .where(RouteStop.route_id == route_id)
        .order_by(RouteStop.stop_sequence)
    )

    return db.scalars(statement).all()

def update_route_stop(db: Session, stop_id: int, data):
    route_stop = db.get(RouteStop, stop_id)

    if route_stop is None:
        return None

    for key, value in data.model_dump().items():
        setattr(route_stop, key, value)

    db.commit()
    db.refresh(route_stop)

    return route_stop

def delete_route_stop(db: Session, stop_id: int):
    route_stop = db.get(RouteStop, stop_id)

    if route_stop is None:
        return False

    db.delete(route_stop)
    db.commit()

    return True