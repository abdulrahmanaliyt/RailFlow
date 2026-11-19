from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class BookingPassenger(Base):
    __tablename__ = "booking_passengers"

    __table_args__ = (
        CheckConstraint(
            "age >= 0 AND age <= 120",
            name="valid_passenger_age",
        ),
        CheckConstraint(
            "gender IN ('M', 'F', 'OTHER')",
            name="valid_passenger_gender",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    booking_id: Mapped[int] = mapped_column(
        ForeignKey("bookings.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    full_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    age: Mapped[int] = mapped_column(nullable=False)

    gender: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )