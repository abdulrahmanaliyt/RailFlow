
from datetime import date

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.search import TrainSearchPageResponse
from app.services.search_service import (
    search_trains,
    validate_station_codes,
)


router = APIRouter(
    prefix="/search",
    tags=["Train Search"],
)


@router.get(
    "/trains",
    response_model=TrainSearchPageResponse,
    summary="Search trains between two stations",
    description=(
        "Search active trains with scheduled journeys "
        "between two stations on a specified date. "
        "Supports pagination."
    ),
    response_description="Paginated matching train results",
)
def search_train_api(
    origin: str = Query(
        min_length=2,
        max_length=10,
        description="Origin station code, e.g. NDLS",
    ),
    destination: str = Query(
        min_length=2,
        max_length=10,
        description="Destination station code, e.g. MMCT",
    ),
    journey_date: date = Query(
        description="Journey date in YYYY-MM-DD format",
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Number of results per page (maximum 100)",
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Number of matching results to skip",
    ),
    db: Session = Depends(get_db),
):
    try:
        validate_station_codes(
            db=db,
            origin_code=origin,
            destination_code=destination,
        )

        return search_trains(
            db=db,
            origin_code=origin,
            destination_code=destination,
            journey_date=journey_date,
            limit=limit,
            offset=offset,
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
