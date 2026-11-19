
from datetime import date, datetime

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TrainSchedule(Base):
    __tablename__ = "train_schedules"

    __table_args__ = (
        UniqueConstraint(
            "route_id",
            "scheduled_departure_at",
            name="uq_train_schedules_route_departure"
        ),
        CheckConstraint(
            "scheduled_arrival_at > scheduled_departure_at",
            name="valid_schedule_arrival"
        ),
        CheckConstraint(
            "status IN ('SCHEDULED', 'CANCELLED', 'COMPLETED')",
            name="valid_schedule_status"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    route_id: Mapped[int] = mapped_column(
        ForeignKey("train_routes.id", ondelete="RESTRICT"),
        nullable=False
    )

    journey_date: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    scheduled_departure_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    scheduled_arrival_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="SCHEDULED",
        server_default="SCHEDULED",
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    route: Mapped["TrainRoute"] = relationship(
        back_populates="schedules"
    )
