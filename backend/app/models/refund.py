from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Refund(Base):
    __tablename__ = "refunds"

    __table_args__ = (
        CheckConstraint(
            "status IN ('INITIATED', 'SUCCESS', 'FAILED')",
            name="valid_refund_status",
        ),
        CheckConstraint(
            "amount >= 0",
            name="nonnegative_refund_amount",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    payment_id: Mapped[int] = mapped_column(
        ForeignKey("payments.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    cancellation_id: Mapped[int] = mapped_column(
        ForeignKey("cancellations.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
    )

    refund_reference: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="INITIATED",
        server_default="INITIATED",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )