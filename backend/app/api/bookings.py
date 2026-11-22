from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user

from app.models.user import User

from app.schemas.booking import (
    BookingCreate,
    BookingResponse
)

from app.services import booking_service as service


router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"]
)


# --------------------------------------------------
# Create booking
# --------------------------------------------------

@router.post(
    "/",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a booking",
    description=(
        "Creates a booking for an authenticated passenger "
        "and temporarily holds the selected seats."
    )
)
def create_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    try:

        return service.create_booking(
            db=db,
            current_user=current_user,
            booking_data=booking_data
        )

    except service.BookingNotFoundError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc)
        ) from exc

    except service.BookingValidationError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        ) from exc

    except service.BookingConflictError as exc:

        raise HTTPException(
            status_code=409,
            detail=str(exc)
        ) from exc


# --------------------------------------------------
# Get current user's bookings
# --------------------------------------------------

@router.get(
    "/my",
    response_model=list[BookingResponse],
    summary="Get my bookings",
    description="Returns the bookings belonging to the authenticated user."
)
def get_my_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return service.get_my_bookings(
        db=db,
        current_user=current_user
    )


# --------------------------------------------------
# Get a specific booking
# --------------------------------------------------

@router.get(
    "/{booking_id}",
    response_model=BookingResponse,
    summary="Get booking details",
    description="Returns booking details if the booking belongs to the authenticated user."
)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    try:

        return service.get_booking_by_id(
            db=db,
            booking_id=booking_id,
            current_user=current_user
        )

    except service.BookingNotFoundError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc)
        ) from exc