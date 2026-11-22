from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Cancellation(Base):
    __tablename__ = "cancellations"

    __table_args__ = (
        CheckConstraint(
            "status IN ('REQUESTED', 'COMPLETED')",
            name="valid_cancellation_status",
        ),
        CheckConstraint(
            "refund_amount >= 0",
            name="nonnegative_cancellation_refund",
        ),
        UniqueConstraint(
            "booking_id",
            "passenger_id",
            name="unique_passenger_cancellation",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    booking_id: Mapped[int] = mapped_column(
        ForeignKey("bookings.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    passenger_id: Mapped[int] = mapped_column(
        ForeignKey("booking_passengers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    refund_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="REQUESTED",
        server_default="REQUESTED",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )