
from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RouteSegment(Base):
    __tablename__ = "route_segments"

    __table_args__ = (
        UniqueConstraint(
            "route_id",
            "segment_sequence",
            name="uq_route_segments_route_sequence",
        ),
        UniqueConstraint(
            "from_route_stop_id",
            "to_route_stop_id",
            name="uq_route_segments_stop_pair",
        ),
        CheckConstraint(
            "from_route_stop_id != to_route_stop_id",
            name="different_segment_stops",
        ),
        CheckConstraint(
            "segment_sequence > 0",
            name="positive_segment_sequence",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    route_id: Mapped[int] = mapped_column(
        ForeignKey("train_routes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    from_route_stop_id: Mapped[int] = mapped_column(
        ForeignKey("route_stops.id", ondelete="RESTRICT"),
        nullable=False,
    )

    to_route_stop_id: Mapped[int] = mapped_column(
        ForeignKey("route_stops.id", ondelete="RESTRICT"),
        nullable=False,
    )

    segment_sequence: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
