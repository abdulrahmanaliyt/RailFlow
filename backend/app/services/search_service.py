
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session, aliased

from app.models import (
    RouteStop,
    Station,
    Train,
    TrainRoute,
    TrainSchedule,
)


def validate_station_codes(
    db: Session,
    origin_code: str,
    destination_code: str,
):
    origin_code = origin_code.strip().upper()
    destination_code = destination_code.strip().upper()

    if origin_code == destination_code:
        raise ValueError(
            "Origin and destination cannot be the same station."
        )

    origin = db.scalar(
        select(Station).where(
            Station.station_code == origin_code
        )
    )

    if origin is None:
        raise LookupError(
            f"Origin station '{origin_code}' not found."
        )

    destination = db.scalar(
        select(Station).where(
            Station.station_code == destination_code
        )
    )

    if destination is None:
        raise LookupError(
            f"Destination station '{destination_code}' not found."
        )

    return origin, destination


def search_trains(
    db: Session,
    origin_code: str,
    destination_code: str,
    journey_date: date,
    limit: int = 20,
    offset: int = 0,
):
    origin_stop = aliased(RouteStop)
    destination_stop = aliased(RouteStop)

    origin_station = aliased(Station)
    destination_station = aliased(Station)

    # Shared query conditions
    conditions = (
        origin_station.station_code == origin_code.strip().upper(),
        destination_station.station_code
        == destination_code.strip().upper(),

        origin_stop.stop_sequence
        < destination_stop.stop_sequence,

        TrainSchedule.journey_date == journey_date,
        TrainSchedule.status == "SCHEDULED",
        Train.is_active.is_(True),
    )

    # Build the common FROM and JOIN structure.
    # Both the count and result queries use the same joins.
    base_statement = (
        select(TrainSchedule.id)
        .select_from(TrainSchedule)
        .join(
            TrainRoute,
            TrainSchedule.route_id == TrainRoute.id,
        )
        .join(
            Train,
            TrainRoute.train_id == Train.id,
        )
        .join(
            origin_stop,
            origin_stop.route_id == TrainRoute.id,
        )
        .join(
            origin_station,
            origin_station.id == origin_stop.station_id,
        )
        .join(
            destination_stop,
            destination_stop.route_id == TrainRoute.id,
        )
        .join(
            destination_station,
            destination_station.id == destination_stop.station_id,
        )
        .where(*conditions)
    )

    # Count all matching schedules before pagination.
    count_statement = select(
        func.count()
    ).select_from(
        base_statement.subquery()
    )

    total = db.scalar(count_statement) or 0

    # Retrieve only the columns required by the API.
    result_statement = (
        select(
            TrainSchedule.id.label("schedule_id"),

            Train.id.label("train_id"),
            Train.train_number.label("train_number"),
            Train.train_name.label("train_name"),

            TrainRoute.id.label("route_id"),
            TrainRoute.route_name.label("route_name"),

            origin_station.station_code.label(
                "origin_station_code"
            ),
            origin_station.name.label(
                "origin_station_name"
            ),
            origin_stop.stop_sequence.label(
                "origin_sequence"
            ),

            destination_station.station_code.label(
                "destination_station_code"
            ),
            destination_station.name.label(
                "destination_station_name"
            ),
            destination_stop.stop_sequence.label(
                "destination_sequence"
            ),

            TrainSchedule.journey_date.label("journey_date"),
            TrainSchedule.scheduled_departure_at.label(
                "scheduled_departure_at"
            ),
            TrainSchedule.scheduled_arrival_at.label(
                "scheduled_arrival_at"
            ),
            TrainSchedule.status.label("status"),
        )
        .select_from(TrainSchedule)
        .join(
            TrainRoute,
            TrainSchedule.route_id == TrainRoute.id,
        )
        .join(
            Train,
            TrainRoute.train_id == Train.id,
        )
        .join(
            origin_stop,
            origin_stop.route_id == TrainRoute.id,
        )
        .join(
            origin_station,
            origin_station.id == origin_stop.station_id,
        )
        .join(
            destination_stop,
            destination_stop.route_id == TrainRoute.id,
        )
        .join(
            destination_station,
            destination_station.id == destination_stop.station_id,
        )
        .where(*conditions)
        # Stable ordering is important for pagination.
        .order_by(
            TrainSchedule.scheduled_departure_at,
            TrainSchedule.id,
        )
        .limit(limit)
        .offset(offset)
    )

    rows = db.execute(result_statement).mappings().all()

    return {
        "items": [dict(row) for row in rows],
        "total": total,
        "limit": limit,
        "offset": offset,
    }
