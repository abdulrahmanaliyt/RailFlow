import sqlalchemy as sa

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Train(Base):

    __tablename__ = "trains"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    train_number: Mapped[str] = mapped_column(
        String(10),
        unique=True,
        nullable=False
    )

    train_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=sa.true(),
        nullable=False
    )
    
    routes: Mapped[list["TrainRoute"]] = relationship(
    back_populates="train"
    )