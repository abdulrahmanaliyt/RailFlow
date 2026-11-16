from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.route_stop import (
    RouteStopCreate,
    RouteStopUpdate,
    RouteStopResponse,
)
from app.services import route_stop_service

router = APIRouter(
    prefix="/route-stops",
    tags=["Route Stops"]
)

@router.post(
    "/",
    response_model=RouteStopResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a station to a train route",
    description="Creates a route stop with a station and its sequence number.",
    response_description="The newly created route stop."
)
def create_route_stop(
    data: RouteStopCreate,
    db: Session = Depends(get_db)
):
    try:
        return route_stop_service.create_route_stop(db, data)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Invalid route/station or duplicate stop sequence/station."
        )

@router.get(
    "/",
    response_model=list[RouteStopResponse],
    summary="Get all route stops",
    description="Returns all route stops ordered by route and sequence.",
    response_description="List of route stops."
)
def get_all_route_stops(db: Session = Depends(get_db)):
    return route_stop_service.get_all_route_stops(db)

@router.get(
    "/{stop_id}",
    response_model=RouteStopResponse,
    summary="Get a route stop",
    description="Finds a route stop using its ID.",
    response_description="The requested route stop."
)
def get_route_stop(
    stop_id: int,
    db: Session = Depends(get_db)
):
    stop = route_stop_service.get_route_stop_by_id(db, stop_id)

    if stop is None:
        raise HTTPException(status_code=404, detail="Route stop not found")

    return stop

@router.get(
    "/route/{route_id}",
    response_model=list[RouteStopResponse],
    summary="Get stops of a route",
    description="Returns the stations belonging to a route in sequence order.",
    response_description="Ordered route stops."
)
def get_stops_by_route(
    route_id: int,
    db: Session = Depends(get_db)
):
    return route_stop_service.get_stops_by_route(db, route_id)

@router.put(
    "/{stop_id}",
    response_model=RouteStopResponse,
    summary="Update a route stop",
    description="Updates the station or sequence of an existing route stop.",
    response_description="The updated route stop."
)
def update_route_stop(
    stop_id: int,
    data: RouteStopUpdate,
    db: Session = Depends(get_db)
):
    try:
        stop = route_stop_service.update_route_stop(db, stop_id, data)

        if stop is None:
            raise HTTPException(status_code=404, detail="Route stop not found")

        return stop

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Duplicate station or sequence in this route."
        )

@router.delete(
    "/{stop_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a route stop",
    description="Removes a station from its route.",
    response_description="Route stop deleted successfully."
)
def delete_route_stop(
    stop_id: int,
    db: Session = Depends(get_db)
):
    deleted = route_stop_service.delete_route_stop(db, stop_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Route stop not found")