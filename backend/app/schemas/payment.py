from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict


class PaymentCreate(BaseModel):
    payment_method: str = Field(
        pattern="^(UPI|CARD|NET_BANKING)$"
    )

    simulate_result: str = Field(
        pattern="^(SUCCESS|FAILED)$"
    )


class PaymentResponse(BaseModel):
    id: int
    booking_id: int
    transaction_reference: str
    amount: Decimal
    payment_method: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaymentHistoryResponse(BaseModel):
    booking_id: int
    payments: list[PaymentResponse]