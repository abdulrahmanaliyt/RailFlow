from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.route import RouteResponse

from app.services.route_service import (
    get_all_routes,
    get_route_by_id,
)


router = APIRouter(
    prefix="/routes",
    tags=["Routes"],
)


# GET ACTIVE ROUTES
@router.get(
    "/",
    response_model=list[RouteResponse],
)
def read_routes(
    db: Session = Depends(get_db),
):
    return get_all_routes(
        db,
        include_inactive=False,
    )


# GET ACTIVE ROUTE BY ID
@router.get(
    "/{route_id}",
    response_model=RouteResponse,
)
def read_route(
    route_id: int,
    db: Session = Depends(get_db),
):
    route = get_route_by_id(
        db,
        route_id,
        active_only=True,
    )

    if route is None:
        raise HTTPException(
            status_code=404,
            detail="Route not found.",
        )

    return route