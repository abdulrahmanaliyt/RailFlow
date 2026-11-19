from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TrainRoute(Base):
    __tablename__ = "train_routes"

    __table_args__ = (
        UniqueConstraint(
            "train_id",
            "route_name",
            name="uq_train_routes_train_id_route_name"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    train_id: Mapped[int] = mapped_column(
        ForeignKey("trains.id", ondelete="RESTRICT"),
        nullable=False
    )

    route_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )
    
    train: Mapped["Train"] = relationship(
        back_populates="routes"
    )

    route_stops: Mapped[list["RouteStop"]] = relationship(
        back_populates="route",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    
    schedules: Mapped[list["TrainSchedule"]] = relationship(
        back_populates="route"
    )