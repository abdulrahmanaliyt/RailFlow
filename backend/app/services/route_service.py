
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Train, TrainRoute
from app.schemas.route import RouteCreate, RouteUpdate


def create_route(db: Session, route_data: RouteCreate):

    train = db.get(Train, route_data.train_id)

    if train is None:
        raise LookupError("Train not found.")

    if not train.is_active:
        raise ValueError("Cannot create a route for an inactive train.")

    route = TrainRoute(**route_data.model_dump())

    db.add(route)
    db.commit()
    db.refresh(route)

    return route

def get_all_routes(db: Session):
    statement = select(TrainRoute).order_by(TrainRoute.id)
    return db.scalars(statement).all()


def get_route_by_id(db: Session, route_id: int):
    return db.get(TrainRoute, route_id)


def update_route(
    db: Session,
    route_id: int,
    route_data: RouteUpdate
):
    route = db.get(TrainRoute, route_id)

    if route is None:
        return None

    for field, value in route_data.model_dump().items():
        setattr(route, field, value)

    db.commit()
    db.refresh(route)

    return route


def delete_route(db: Session, route_id: int):
    route = db.get(TrainRoute, route_id)

    if route is None:
        return False

    db.delete(route)
    db.commit()

    return True
