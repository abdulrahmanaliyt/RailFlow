from sqlalchemy import select
from sqlalchemy.orm import Session, aliased

from app.models import (
    RouteStop,
    Station,
    Train,
    TrainRoute,
    TrainSchedule,
)
from app.schemas.train_search import TrainSearchResult
from app.services.availability_service import get_available_seats


def search_trains(
    db: Session,
    from_station_code: str,
    to_station_code: str,
    journey_date,
    limit: int = 20,
    offset: int = 0,
):
    # Normalize station codes for case-insensitive matching
    from_station_code = from_station_code.strip().upper()
    to_station_code = to_station_code.strip().upper()

    # Reject identical origin and destination codes before querying
    if from_station_code == to_station_code:
        raise ValueError(
            "Origin and destination stations must be different."
        )

    # Create aliases so route_stops and stations can each be joined twice
    OriginStop = aliased(RouteStop)
    DestinationStop = aliased(RouteStop)

    OriginStation = aliased(Station)
    DestinationStation = aliased(Station)

    # Find active origin and destination stations
    origin_station = db.scalar(
        select(Station).where(
            Station.station_code == from_station_code,
            Station.is_active.is_(True),
        )
    )

    if origin_station is None:
        raise LookupError(
            f"Origin station '{from_station_code}' not found."
        )

    destination_station = db.scalar(
        select(Station).where(
            Station.station_code == to_station_code,
            Station.is_active.is_(True),
        )
    )

    if destination_station is None:
        raise LookupError(
            f"Destination station '{to_station_code}' not found."
        )

    # Ensure distinct stations by ID as well
    if origin_station.id == destination_station.id:
        raise ValueError(
            "Origin and destination stations must be different."
        )

    # Build the search query across schedules, routes, trains, stops, and stations
    statement = (
        select(
            TrainSchedule,
            TrainRoute,
            Train,
            OriginStop,
            DestinationStop,
            OriginStation,
            DestinationStation,
        )
        .join(
            TrainRoute,
            TrainSchedule.route_id == TrainRoute.id,
        )
        .join(
            Train,
            TrainRoute.train_id == Train.id,
        )
        .join(
            OriginStop,
            OriginStop.route_id == TrainRoute.id,
        )
        .join(
            OriginStation,
            OriginStop.station_id == OriginStation.id,
        )
        .join(
            DestinationStop,
            DestinationStop.route_id == TrainRoute.id,
        )
        .join(
            DestinationStation,
            DestinationStop.station_id == DestinationStation.id,
        )
        .where(
            OriginStation.id == origin_station.id,
            DestinationStation.id == destination_station.id,
            OriginStop.stop_sequence < DestinationStop.stop_sequence,
            TrainSchedule.journey_date == journey_date,
            TrainSchedule.status == "SCHEDULED",
            Train.is_active.is_(True),
            TrainRoute.is_active.is_(True),
            OriginStation.is_active.is_(True),
            DestinationStation.is_active.is_(True),
        )
        .order_by(
            TrainSchedule.scheduled_departure_at
        )
        .limit(limit)
        .offset(offset)
    )

    # Execute the query and map ORM entities into TrainSearchResult items
    results = db.execute(statement).all()

    response = []

    for row in results:
        (
            schedule,
            route,
            train,
            origin_stop,
            destination_stop,
            origin_station,
            destination_station,
        ) = row

        availability = get_available_seats(
            db=db,
            schedule_id=schedule.id,
            origin_code=origin_station.station_code,
            destination_code=destination_station.station_code,
        )

        # Keep schedules even when available_seat_count == 0
        response.append(
            TrainSearchResult(
                schedule_id=schedule.id,
                train_id=train.id,
                train_number=train.train_number,
                train_name=train.train_name,
                route_id=route.id,
                from_station_code=origin_station.station_code,
                from_station_name=origin_station.name,
                from_sequence=origin_stop.stop_sequence,
                to_station_code=destination_station.station_code,
                to_station_name=destination_station.name,
                to_sequence=destination_stop.stop_sequence,
                journey_date=schedule.journey_date,
                scheduled_departure_at=(
                    schedule.scheduled_departure_at
                ),
                scheduled_arrival_at=(
                    schedule.scheduled_arrival_at
                ),
                status=schedule.status,
                available_seats=availability["available_seat_count"],
            )
        )

    return response