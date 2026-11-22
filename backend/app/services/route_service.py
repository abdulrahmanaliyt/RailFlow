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

    route = TrainRoute(
        train_id=route_data.train_id,
        route_name=route_data.route_name,
        is_active=True,
    )

    db.add(route)
    db.commit()
    db.refresh(route)

    return route


def get_all_routes(
    db: Session,
    include_inactive: bool = False,
):
    statement = select(TrainRoute).order_by(TrainRoute.id)

    if not include_inactive:
        statement = statement.where(
            TrainRoute.is_active.is_(True)
        )

    return db.scalars(statement).all()


def get_route_by_id(
    db: Session,
    route_id: int,
    active_only: bool = False,
):
    statement = select(TrainRoute).where(
        TrainRoute.id == route_id
    )

    if active_only:
        statement = statement.where(
            TrainRoute.is_active.is_(True)
        )

    return db.scalar(statement)


def update_route(
    db: Session,
    route_id: int,
    route_data: RouteUpdate,
):
    route = db.get(TrainRoute, route_id)

    if route is None:
        return None

    update_data = route_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if value is None:
            raise ValueError(f"{field} cannot be null.")

        setattr(route, field, value)

    db.commit()
    db.refresh(route)

    return route


def set_route_active(
    db: Session,
    route_id: int,
    active: bool,
):
    route = db.get(TrainRoute, route_id)

    if route is None:
        return None

    if active:
        train = db.get(Train, route.train_id)

        if train is None or not train.is_active:
            raise ValueError(
                "Cannot activate a route belonging to an inactive train."
            )

    route.is_active = active

    db.commit()
    db.refresh(route)

    return route