
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Station
from app.schemas.station import StationCreate, StationUpdate


def create_station(db: Session, station_data: StationCreate):
    station = Station(**station_data.model_dump())

    db.add(station)
    db.commit()
    db.refresh(station)

    return station


def get_all_stations(db: Session):
    statement = select(Station).order_by(Station.id)
    return db.scalars(statement).all()


def get_station_by_id(db: Session, station_id: int):
    return db.get(Station, station_id)


def update_station(db: Session, station_id: int, station_data: StationUpdate):
    station = db.get(Station, station_id)
    if not station:
        return None
    
   
    update_data = station_data.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(station, key, value)
        
    db.commit()
    db.refresh(station)
    return station


def delete_station(db: Session, station_id: int):
    station = db.get(Station, station_id)

    if station is None:
        return False

    db.delete(station)
    db.commit()

    return True
