from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.train_search import TrainSearchResult
from app.services import train_search_service

router = APIRouter(
    prefix="/search",
    tags=["Train Search"],
)


@router.get(
    "/trains",
    response_model=list[TrainSearchResult],
    summary="Search trains between two stations",
    description=(
        "Search active trains with scheduled journeys between two stations "
        "on a specific journey date in forward stop sequence."
    ),
)
def search_trains_endpoint(
    from_station: str = Query(
        min_length=2,
        max_length=10,
        description="Origin station code (e.g., NDLS)",
    ),
    to_station: str = Query(
        min_length=2,
        max_length=10,
        description="Destination station code (e.g., BPL)",
    ),
    journey_date: date = Query(
        description="Journey date in YYYY-MM-DD format",
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of results to return",
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Number of matching results to skip",
    ),
    db: Session = Depends(get_db),
):
    try:
        return train_search_service.search_trains(
            db=db,
            from_station_code=from_station,
            to_station_code=to_station,
            journey_date=journey_date,
            limit=limit,
            offset=offset,
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc