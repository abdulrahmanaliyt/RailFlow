from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.route_segment import RouteSegmentResponse
from app.services import route_segment_service as service


router = APIRouter(
    prefix="/routes",
    tags=["Route Segments"],
)


@router.post(
    "/{route_id}/segments/generate",
    response_model=list[RouteSegmentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Generate route segments",
    description=(
        "Creates one segment for each pair of consecutive route stops. "
        "If the same segments already exist, returns them without duplication."
    ),
)
def generate_segments(
    route_id: int,
    db: Session = Depends(get_db),
):
    try:
        return service.generate_route_segments(db, route_id)
    except service.NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except service.ConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get(
    "/{route_id}/segments",
    response_model=list[RouteSegmentResponse],
    summary="List route segments",
)
def list_segments(
    route_id: int,
    db: Session = Depends(get_db),
):
    try:
        return service.get_route_segments(db, route_id)
    except service.NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc