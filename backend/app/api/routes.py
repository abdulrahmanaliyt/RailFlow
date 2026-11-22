
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.dependencies import get_db

from app.schemas.route import (
    RouteCreate,
    RouteUpdate,
    RouteResponse
)

from app.services.route_service import (
    create_route,
    get_all_routes,
    get_route_by_id,
    update_route,
    delete_route
)


router = APIRouter(
    prefix="/routes",
    tags=["Routes"]
)

@router.post(
    "/",
    response_model=RouteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a train route",
    description="Create a route associated with an existing train.",
)
def create_route_endpoint(
    route_data: RouteCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_route(db, route_data)

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
            detail="Invalid train ID or duplicate route name for this train.",
        )

@router.get(
    "/",
    response_model=list[RouteResponse],
    summary="Get all train routes"
)
def read_routes(db: Session = Depends(get_db)):
    return get_all_routes(db)


@router.get(
    "/{route_id}",
    response_model=RouteResponse,
    summary="Get route by ID"
)
def read_route(
    route_id: int,
    db: Session = Depends(get_db)
):
    route = get_route_by_id(db, route_id)

    if route is None:
        raise HTTPException(
            status_code=404,
            detail="Route not found."
        )

    return route


@router.put(
    "/{route_id}",
    response_model=RouteResponse,
    summary="Update train route"
)
def update_route_endpoint(
    route_id: int,
    route_data: RouteUpdate,
    db: Session = Depends(get_db)
):
    try:
        route = update_route(db, route_id, route_data)

        if route is None:
            raise HTTPException(
                status_code=404,
                detail="Route not found."
            )

        return route

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Route update violates a database constraint."
        )


@router.delete(
    "/{route_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete train route"
)
def remove_route(
    route_id: int,
    db: Session = Depends(get_db)
):
    try:
        deleted = delete_route(db, route_id)

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Route not found."
            )

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Cannot delete this route because it is referenced by other records."
        )
