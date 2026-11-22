from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_admin

from app.schemas.route import (
    RouteCreate,
    RouteUpdate,
    RouteResponse,
)

from app.services.route_service import (
    create_route,
    get_all_routes,
    get_route_by_id,
    update_route,
    set_route_active,
)


router = APIRouter(
    prefix="/admin/routes",
    tags=["Admin Routes"],
    dependencies=[Depends(require_admin)],
)


# CREATE ROUTE
@router.post(
    "/",
    response_model=RouteResponse,
    status_code=status.HTTP_201_CREATED,
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
            detail="Duplicate route name for this train.",
        )


# GET ALL ROUTES INCLUDING INACTIVE
@router.get(
    "/",
    response_model=list[RouteResponse],
)
def read_all_routes(
    db: Session = Depends(get_db),
):
    return get_all_routes(
        db,
        include_inactive=True,
    )


# GET ROUTE BY ID
@router.get(
    "/{route_id}",
    response_model=RouteResponse,
)
def read_route(
    route_id: int,
    db: Session = Depends(get_db),
):
    route = get_route_by_id(db, route_id)

    if route is None:
        raise HTTPException(
            status_code=404,
            detail="Route not found.",
        )

    return route


# UPDATE ROUTE
@router.patch(
    "/{route_id}",
    response_model=RouteResponse,
)
def update_route_endpoint(
    route_id: int,
    route_data: RouteUpdate,
    db: Session = Depends(get_db),
):
    try:
        route = update_route(
            db,
            route_id,
            route_data,
        )

        if route is None:
            raise HTTPException(
                status_code=404,
                detail="Route not found.",
            )

        return route

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
            detail="Route update violates a database constraint.",
        )


# DEACTIVATE ROUTE
@router.patch(
    "/{route_id}/deactivate",
    response_model=RouteResponse,
)
def deactivate_route(
    route_id: int,
    db: Session = Depends(get_db),
):
    route = set_route_active(
        db,
        route_id,
        active=False,
    )

    if route is None:
        raise HTTPException(
            status_code=404,
            detail="Route not found.",
        )

    return route


# ACTIVATE ROUTE
@router.patch(
    "/{route_id}/activate",
    response_model=RouteResponse,
)
def activate_route(
    route_id: int,
    db: Session = Depends(get_db),
):
    try:
        route = set_route_active(
            db,
            route_id,
            active=True,
        )

        if route is None:
            raise HTTPException(
                status_code=404,
                detail="Route not found.",
            )

        return route

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        )