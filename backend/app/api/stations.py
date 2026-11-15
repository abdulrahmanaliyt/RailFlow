from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.station import (
    StationCreate,
    StationUpdate,
    StationResponse
)
from app.services.station_service import (
    create_station,
    get_all_stations,
    get_station_by_id,
    update_station,
    delete_station
)

router = APIRouter(
    prefix="/stations",
    tags=["Stations"]
)


# 1. CREATE STATION
@router.post(
    "/",
    response_model=StationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new railway station",
    description="Registers a new railway station in the system with a unique station code, name, city, and state.",
    response_description="The newly created railway station record."
)
def create_station_endpoint(
    station_data: StationCreate,
    db: Session = Depends(get_db)
):
    try:
        return create_station(db, station_data)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Station code already exists or violates a database constraint."
        )


# 2. GET ALL STATIONS
@router.get(
    "/",
    response_model=list[StationResponse],
    summary="Get all railway stations",
    description="Retrieves a complete list of all registered railway stations currently stored in the database.",
    response_description="A list of railway stations."
)
def read_stations(db: Session = Depends(get_db)):
    return get_all_stations(db)


# 3. GET STATION BY ID
@router.get(
    "/{station_id}",
    response_model=StationResponse,
    summary="Get a station by ID",
    description="Retrieves detailed information for a specific railway station using its unique ID identifier.",
    response_description="The requested railway station details."
)
def read_station(
    station_id: int,
    db: Session = Depends(get_db)
):
    station = get_station_by_id(db, station_id)

    if station is None:
        raise HTTPException(
            status_code=404,
            detail="Station not found"
        )

    return station


# 4. UPDATE STATION
@router.put(
    "/{station_id}",
    response_model=StationResponse,
    summary="Update an existing station",
    description="Updates information for an existing railway station by its ID. Supports partial updates via optional fields.",
    response_description="The updated railway station record."
)
def update_station_endpoint(
    station_id: int,
    station_data: StationUpdate,
    db: Session = Depends(get_db)
):
    try:
        station = update_station(db, station_id, station_data)

        if station is None:
            raise HTTPException(
                status_code=404,
                detail="Station not found"
            )

        return station

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Station update violates a database constraint."
        )


# 5. DELETE STATION
@router.delete(
    "/{station_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a station",
    description="Deletes a specified railway station by its unique ID. Returns no content on successful deletion.",
    response_description="Station successfully deleted."
)
def remove_station(
    station_id: int,
    db: Session = Depends(get_db)
):
    try:
        deleted = delete_station(db, station_id)

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Station not found"
            )

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Cannot delete this station because it is referenced by another record."
        )