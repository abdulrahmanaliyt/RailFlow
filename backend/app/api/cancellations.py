from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user

from app.schemas.cancellation import (
    CancellationCreate,
    CancellationResult,
    BookingCancellationResult,
)

from app.services.cancellation_service import (
    cancel_passenger,
    cancel_entire_booking,
    CancellationValidationError,
    CancellationConflictError,
)


router = APIRouter(
    prefix="/bookings",
    tags=["Cancellations"],
)


@router.post(
    "/{booking_id}/passengers/{passenger_id}/cancel",
    response_model=CancellationResult,
)
def cancel_booking_passenger(
    booking_id: int,
    passenger_id: int,
    cancellation_data: CancellationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    try:

        cancellation, refund, booking_status = (
            cancel_passenger(
                db=db,
                booking_id=booking_id,
                passenger_id=passenger_id,
                current_user=current_user,
                cancellation_data=cancellation_data,
            )
        )

        return {
            "message": "Passenger cancellation processed.",
            "booking_status": booking_status,
            "cancellation": cancellation,
            "refund": refund,
        }

    except CancellationValidationError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except CancellationConflictError as exc:

        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )


@router.post(
    "/{booking_id}/cancel",
    response_model=BookingCancellationResult,
)
def cancel_entire_booking_endpoint(
    booking_id: int,
    cancellation_data: CancellationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    try:

        booking, cancellations, refunds = (
            cancel_entire_booking(
                db=db,
                booking_id=booking_id,
                current_user=current_user,
                cancellation_data=cancellation_data,
            )
        )

        return {
            "message": "Booking cancelled successfully.",
            "booking_id": booking.id,
            "booking_status": booking.status,
            "cancellations": cancellations,
            "refunds": refunds,
        }

    except CancellationValidationError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except CancellationConflictError as exc:

        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )