from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.schemas.payment import (
    PaymentCreate,
    PaymentHistoryResponse,
    PaymentResponse,
)
from app.services.payment_service import (
    PaymentConflictError,
    PaymentValidationError,
    get_payment_history,
    process_payment,
)

router = APIRouter(
    prefix="/bookings",
    tags=["Payments"],
)


@router.post(
    "/{booking_id}/pay",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
def pay_for_booking(
    booking_id: int,
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        return process_payment(
            db=db,
            booking_id=booking_id,
            current_user=current_user,
            payment_data=payment_data,
        )
    except PaymentValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except PaymentConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get(
    "/{booking_id}/payments",
    response_model=PaymentHistoryResponse,
    status_code=status.HTTP_200_OK,
)
def get_booking_payments(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        history = get_payment_history(
            db=db,
            booking_id=booking_id,
            current_user=current_user,
        )

        # Normalize either a list of Payment objects or a dict payload
        if isinstance(history, dict):
            payments = history.get("payments", [])
            resolved_booking_id = history.get("booking_id", booking_id)
        else:
            payments = history
            resolved_booking_id = booking_id

        return {
            "booking_id": resolved_booking_id,
            "payments": payments,
        }
    except PaymentValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc