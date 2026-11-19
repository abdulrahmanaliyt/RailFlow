from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.availability import SeatAvailabilityResponse
from app.services import availability_service as service


router = APIRouter(
    prefix="/availability",
    tags=["Seat Availability"],
)


@router.get(
    "/seats",
    response_model=SeatAvailabilityResponse,
    summary="Check available seats",
    description=(
        "Returns active seats for a scheduled train that have no "
        "active reservations on any segment between the requested "
        "origin and destination."
    ),
    response_description="Available seats for the requested journey.",
)
def check_seat_availability(
    schedule_id: Annotated[
        int,
        Query(
            gt=0,
            description="ID of the scheduled train journey.",
        ),
    ],
    origin: Annotated[
        str,
        Query(
            min_length=2,
            max_length=10,
            description="Origin station code, for example NDLS.",
        ),
    ],
    destination: Annotated[
        str,
        Query(
            min_length=2,
            max_length=10,
            description="Destination station code, for example BPL.",
        ),
    ],
    coach_type: Annotated[
        str | None,
        Query(
            min_length=2,
            max_length=10,
            description="Optional coach type filter, for example 3A or SL.",
        ),
    ] = None,
    db: Session = Depends(get_db),
):
    try:
        return service.get_available_seats(
            db=db,
            schedule_id=schedule_id,
            origin_code=origin,
            destination_code=destination,
            coach_type=coach_type,
        )

    except service.NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except service.ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except service.ConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc