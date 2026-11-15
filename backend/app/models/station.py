from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Station(Base):

    __tablename__ = "stations"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    station_code: Mapped[str] = mapped_column(
        String(10),
        unique=True,
        nullable=False
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    city: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    state: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    
    route_stops: Mapped[list["RouteStop"]] = relationship(
        back_populates="station"
    )