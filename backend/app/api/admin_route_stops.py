from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_admin

from app.schemas.route_stop import (
    RouteStopCreate,
    RouteStopUpdate,
    RouteStopResponse,
)

from app.services import route_stop_service


router = APIRouter(
    prefix="/admin/route-stops",
    tags=["Admin Route Stops"],
    dependencies=[Depends(require_admin)],
)


# CREATE ROUTE STOP
@router.post(
    "/",
    response_model=RouteStopResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_route_stop(
    data: RouteStopCreate,
    db: Session = Depends(get_db),
):
    try:
        return route_stop_service.create_route_stop(db, data)

    except LookupError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        )

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Duplicate station or sequence in this route.",
        )


# GET ALL ROUTE STOPS
@router.get(
    "/",
    response_model=list[RouteStopResponse],
)
def read_all_route_stops(
    db: Session = Depends(get_db),
):
    return route_stop_service.get_all_route_stops(db)


# GET ROUTE STOPS BY ROUTE
@router.get(
    "/route/{route_id}",
    response_model=list[RouteStopResponse],
)
def read_stops_by_route(
    route_id: int,
    db: Session = Depends(get_db),
):
    if not route_stop_service.route_exists(db, route_id):
        raise HTTPException(
            status_code=404,
            detail="Train route not found.",
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

    return stop


# UPDATE ROUTE STOP
@router.patch(
    "/{stop_id}",
    response_model=RouteStopResponse,
)
def update_route_stop(
    stop_id: int,
    data: RouteStopUpdate,
    db: Session = Depends(get_db),
):
    try:
        stop = route_stop_service.update_route_stop(
            db,
            stop_id,
            data,
        )

        if stop is None:
            raise HTTPException(
                status_code=404,
                detail="Route stop not found.",
            )

        return stop

    except LookupError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except ValueError as exc:
        db.rollback()

        raise HTTPException(
            status_code=422,
            detail=str(exc),
        )

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Duplicate station or sequence in this route.",
        )


# DELETE ROUTE STOP
@router.delete(
    "/{stop_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_route_stop(
    stop_id: int,
    db: Session = Depends(get_db),
):
    try:
        deleted = route_stop_service.delete_route_stop(
            db,
            stop_id,
        )

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Route stop not found.",
            )

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        )