
from sqlalchemy import (
    Boolean,
    ForeignKey,
    String,
    UniqueConstraint,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Coach(Base):
    __tablename__ = "coaches"

    __table_args__ = (
        UniqueConstraint(
            "train_id",
            "coach_number",
            name="uq_coaches_train_coach_number",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    train_id: Mapped[int] = mapped_column(
        ForeignKey("trains.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    coach_number: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    coach_type: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=true(),
    )
