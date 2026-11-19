from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SeatSegmentReservation(Base):
    __tablename__ = "seat_segment_reservations"

    __table_args__ = (
        CheckConstraint(
            "status IN ('HELD', 'CONFIRMED', 'CANCELLED', 'EXPIRED')",
            name="valid_reservation_status",
        ),
        CheckConstraint(
            "status != 'HELD' OR expires_at IS NOT NULL",
            name="held_reservation_requires_expiry",
        ),
        Index(
            "uq_active_seat_segment",
            "schedule_id",
            "seat_id",
            "route_segment_id",
            unique=True,
            postgresql_where=text(
                "status IN ('HELD', 'CONFIRMED')"
            ),
        ),
        Index("ix_reservations_booking_id", "booking_id"),
        Index("ix_reservations_passenger_id", "passenger_id"),
        Index(
            "ix_reservations_schedule_segment",
            "schedule_id",
            "route_segment_id",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    booking_id: Mapped[int] = mapped_column(
        ForeignKey("bookings.id", ondelete="RESTRICT"),
        nullable=False,
    )

    passenger_id: Mapped[int] = mapped_column(
        ForeignKey("booking_passengers.id", ondelete="RESTRICT"),
        nullable=False,
    )

    schedule_id: Mapped[int] = mapped_column(
        ForeignKey("train_schedules.id", ondelete="RESTRICT"),
        nullable=False,
    )

    seat_id: Mapped[int] = mapped_column(
        ForeignKey("seats.id", ondelete="RESTRICT"),
        nullable=False,
    )

    route_segment_id: Mapped[int] = mapped_column(
        ForeignKey("route_segments.id", ondelete="RESTRICT"),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="HELD",
        server_default=text("'HELD'"),
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )