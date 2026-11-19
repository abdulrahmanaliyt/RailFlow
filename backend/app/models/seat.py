
from sqlalchemy import (
    Boolean,
    ForeignKey,
    String,
    UniqueConstraint,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Seat(Base):
    __tablename__ = "seats"

    __table_args__ = (
        UniqueConstraint(
            "coach_id",
            "seat_number",
            name="uq_seats_coach_seat_number",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    coach_id: Mapped[int] = mapped_column(
        ForeignKey("coaches.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    seat_number: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    berth_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=true(),
    )
