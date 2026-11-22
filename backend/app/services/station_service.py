from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Station
from app.schemas.station import StationCreate, StationUpdate


def create_station(db: Session, station_data: StationCreate):

    station = Station(
        **station_data.model_dump(),
        is_active=True,
    )

    db.add(station)
    db.commit()
    db.refresh(station)

    return station


def get_all_stations(db: Session, include_inactive=False):

    statement = select(Station).order_by(Station.name)

    if not include_inactive:
        statement = statement.where(
            Station.is_active.is_(True)
        )

    return db.scalars(statement).all()


def get_station_by_id(db: Session, station_id: int):

    return db.get(Station, station_id)


def update_station(db: Session, station_id: int, station_data: StationUpdate):

    station = db.get(Station, station_id)

    if station is None:
        return None

    update_data = station_data.model_dump(
        exclude_unset=True
    )

    # Reject explicitly supplied null values.
    if any(value is None for value in update_data.values()):
        raise ValueError(
            "Station fields cannot be set to null."
        )

    for key, value in update_data.items():
        setattr(station, key, value)

    db.commit()
    db.refresh(station)

    return station


def set_station_active(db: Session, station_id: int, active: bool):

    station = db.get(Station, station_id)

    if station is None:
        return None

    station.is_active = active

    db.commit()
    db.refresh(station)

    return station