from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.train_route import TrainRoute
from app.models.route_stop import RouteStop
from app.models.route_segment import RouteSegment


class NotFoundError(Exception):
    pass


class ConflictError(Exception):
    pass


def generate_route_segments(db: Session, route_id: int):
    route = db.get(TrainRoute, route_id)

    if not route:
        raise NotFoundError("Route not found.")

    stops_statement = (
        select(RouteStop)
        .where(RouteStop.route_id == route_id)
        .order_by(RouteStop.stop_sequence)
    )
    stops = db.scalars(stops_statement).all()

    if len(stops) < 2:
        raise ConflictError(
            "At least two route stops are required to generate segments."
        )

    expected = [
        (
            stops[index].id,
            stops[index + 1].id,
            index + 1,
        )
        for index in range(len(stops) - 1)
    ]

    existing_statement = (
        select(RouteSegment)
        .where(RouteSegment.route_id == route_id)
        .order_by(RouteSegment.segment_sequence)
    )
    existing = db.scalars(existing_statement).all()

    existing_values = [
        (
            segment.from_route_stop_id,
            segment.to_route_stop_id,
            segment.segment_sequence,
        )
        for segment in existing
    ]

    if existing:
        if existing_values == expected:
            return existing

        raise ConflictError(
            "Segments already exist but do not match the current route stops. "
            "Do not regenerate automatically because existing segments may "
            "be referenced by reservations."
        )

    segments = [
        RouteSegment(
            route_id=route_id,
            from_route_stop_id=from_stop_id,
            to_route_stop_id=to_stop_id,
            segment_sequence=sequence,
        )
        for from_stop_id, to_stop_id, sequence in expected
    ]

    try:
        db.add_all(segments)
        db.commit()

        for segment in segments:
            db.refresh(segment)

        return segments

    except Exception:
        db.rollback()
        raise


def get_route_segments(db: Session, route_id: int):
    if not db.get(TrainRoute, route_id):
        raise NotFoundError("Route not found.")

    statement = (
        select(RouteSegment)
        .where(RouteSegment.route_id == route_id)
        .order_by(RouteSegment.segment_sequence)
    )

    return db.scalars(statement).all()