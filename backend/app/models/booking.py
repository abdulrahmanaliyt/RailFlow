from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from decimal import Decimal

from app.db.base import Base


class Booking(Base):
    __tablename__ = "bookings"

    __table_args__ = (
        CheckConstraint(
            "status IN ('PENDING_PAYMENT', 'CONFIRMED', 'CANCELLED')",
            name="valid_booking_status",
        ),
        CheckConstraint(
            "total_amount >= 0",
            name="nonnegative_booking_amount",
        ),
        Index("ix_bookings_user_id", "user_id"),
        Index("ix_bookings_schedule_id", "schedule_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    pnr: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        unique=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )

    schedule_id: Mapped[int] = mapped_column(
        ForeignKey("train_schedules.id", ondelete="RESTRICT"),
        nullable=False,
    )

    from_route_stop_id: Mapped[int] = mapped_column(
        ForeignKey("route_stops.id", ondelete="RESTRICT"),
        nullable=False,
    )

    to_route_stop_id: Mapped[int] = mapped_column(
        ForeignKey("route_stops.id", ondelete="RESTRICT"),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="PENDING_PAYMENT",
        server_default=text("'PENDING_PAYMENT'"),
    )

    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00"),
        server_default=text("0"),
)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
)