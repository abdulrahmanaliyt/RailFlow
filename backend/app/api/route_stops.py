from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.route_stop import RouteStopResponse
from app.services import route_stop_service

router = APIRouter(
    prefix="/route-stops",
    tags=["Route Stops"],
)


# GET ROUTE STOPS BY ROUTE
@router.get(
    "/route/{route_id}",
    response_model=list[RouteStopResponse],
)
def read_stops_by_route(
    route_id: int,
    db: Session = Depends(get_db),
):
    route = route_stop_service.get_active_route(db, route_id)

    if route is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active train route not found.",
        )

    return route_stop_service.get_stops_by_route(
        db,
        route_id,
    )


# GET ROUTE STOP BY ID
@router.get(
    "/{stop_id}",
    response_model=RouteStopResponse,
)
def read_route_stop(
    stop_id: int,
    db: Session = Depends(get_db),
):
    stop = route_stop_service.get_route_stop_by_id(
        db,
        stop_id,
    )

    if stop is None:
        raise HTTPException(
            status_code=404,
            detail="Route stop not found.",
        )

    route = route_stop_service.get_active_route(
        db,
        stop.route_id,
    )

    if route is None:
        raise HTTPException(
            status_code=404,
            detail="Active train route not found.",
        )

    return stop