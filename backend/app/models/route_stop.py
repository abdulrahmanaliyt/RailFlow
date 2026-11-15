from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Integer,
    UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RouteStop(Base):
    __tablename__ = "route_stops"

    __table_args__ = (
        UniqueConstraint(
            "route_id",
            "stop_sequence",
            name="uq_route_stops_route_id_stop_sequence"
        ),
        CheckConstraint(
            "stop_sequence > 0",
            name="positive_stop_sequence"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    route_id: Mapped[int] = mapped_column(
        ForeignKey("train_routes.id", ondelete="CASCADE"),
        nullable=False
    )

    station_id: Mapped[int] = mapped_column(
        ForeignKey("stations.id", ondelete="RESTRICT"),
        nullable=False
    )

    stop_sequence: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    
    route: Mapped["TrainRoute"] = relationship(
        back_populates="route_stops"
    )

    station: Mapped["Station"] = relationship(
        back_populates="route_stops"
    )