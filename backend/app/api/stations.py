from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db

from app.schemas.station import StationResponse

from app.services.station_service import (
    get_all_stations,
    get_station_by_id,
)


router = APIRouter(
    prefix="/stations",
    tags=["Stations"],
)


# Public: list active stations
@router.get(
    "/",
    response_model=list[StationResponse],
)
def read_stations(
    db: Session = Depends(get_db),
):

    return get_all_stations(
        db,
        include_inactive=False,
    )


# Public: get one active station
@router.get(
    "/{station_id}",
    response_model=StationResponse,
)
def read_station(
    station_id: int,
    db: Session = Depends(get_db),
):

    station = get_station_by_id(
        db,
        station_id,
    )

    if station is None or not station.is_active:
        raise HTTPException(
            status_code=404,
            detail="Station not found.",
        )

    return station