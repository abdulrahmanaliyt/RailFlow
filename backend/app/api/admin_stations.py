from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_admin

from app.schemas.station import (
    StationCreate,
    StationUpdate,
    StationResponse,
)

from app.services.station_service import (
    create_station,
    get_all_stations,
    get_station_by_id,
    update_station,
    set_station_active,
)


router = APIRouter(
    prefix="/admin/stations",
    tags=["Admin Stations"],
)


# CREATE
@router.post(
    "/",
    response_model=StationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_station_endpoint(
    station_data: StationCreate,
    db: Session = Depends(get_db),
    admin_user=Depends(require_admin),
):

    try:
        return create_station(db, station_data)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Station code already exists.",
        )


# LIST ALL
@router.get(
    "/",
    response_model=list[StationResponse],
)
def list_stations_endpoint(
    db: Session = Depends(get_db),
    admin_user=Depends(require_admin),
):

    return get_all_stations(
        db,
        include_inactive=True,
    )


# GET BY ID
@router.get(
    "/{station_id}",
    response_model=StationResponse,
)
def get_station_endpoint(
    station_id: int,
    db: Session = Depends(get_db),
    admin_user=Depends(require_admin),
):

    station = get_station_by_id(
        db,
        station_id,
    )

    if station is None:
        raise HTTPException(
            status_code=404,
            detail="Station not found.",
        )

    return station


# UPDATE
@router.patch(
    "/{station_id}",
    response_model=StationResponse,
)
def update_station_endpoint(
    station_id: int,
    station_data: StationUpdate,
    db: Session = Depends(get_db),
    admin_user=Depends(require_admin),
):

    try:

        station = update_station(
            db,
            station_id,
            station_data,
        )

        if station is None:
            raise HTTPException(
                status_code=404,
                detail="Station not found.",
            )

        return station

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Station code already exists.",
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        )


# DEACTIVATE
@router.patch(
    "/{station_id}/deactivate",
    response_model=StationResponse,
)
def deactivate_station_endpoint(
    station_id: int,
    db: Session = Depends(get_db),
    admin_user=Depends(require_admin),
):

    station = set_station_active(
        db,
        station_id,
        False,
    )

    if station is None:
        raise HTTPException(
            status_code=404,
            detail="Station not found.",
        )

    return station


# ACTIVATE
@router.patch(
    "/{station_id}/activate",
    response_model=StationResponse,
)
def activate_station_endpoint(
    station_id: int,
    db: Session = Depends(get_db),
    admin_user=Depends(require_admin),
):

    station = set_station_active(
        db,
        station_id,
        True,
    )

    if station is None:
        raise HTTPException(
            status_code=404,
            detail="Station not found.",
        )

    return station