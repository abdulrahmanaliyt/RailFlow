from decimal import Decimal
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class CancellationCreate(BaseModel):
    reason: str | None = Field(
        default=None,
        max_length=500,
    )

    simulate_refund_result: str = Field(
        default="SUCCESS",
        pattern="^(SUCCESS|FAILED)$",
    )


class CancellationResponse(BaseModel):
    id: int
    booking_id: int
    passenger_id: int
    reason: str | None
    refund_amount: Decimal
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RefundResponse(BaseModel):
    id: int
    payment_id: int
    cancellation_id: int
    refund_reference: str
    amount: Decimal
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CancellationResult(BaseModel):
    message: str
    booking_status: str
    cancellation: CancellationResponse
    refund: RefundResponse | None


class BookingCancellationResult(BaseModel):
    message: str
    booking_id: int
    booking_status: str
    cancellations: list[CancellationResponse]
    refunds: list[RefundResponse]