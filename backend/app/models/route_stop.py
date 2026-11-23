from sqlalchemy import CheckConstraint, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RouteStop(Base):
    __tablename__ = "route_stops"
    __table_args__ = (
        UniqueConstraint(
            "route_id",
            "stop_sequence",
            name="uq_route_stops_route_id_stop_sequence",
        ),
        UniqueConstraint(
            "route_id",
            "station_id",
            name="uq_route_stops_route_id_station_id",
        ),
        CheckConstraint(
            "stop_sequence > 0",
            name="ck_route_stops_stop_sequence_positive",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    route_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("train_routes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    station_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("stations.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    stop_sequence: Mapped[int] = mapped_column(Integer, nullable=False)

    route = relationship("TrainRoute")
    station = relationship("Station")