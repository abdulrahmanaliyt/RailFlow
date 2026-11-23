from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models import TrainSchedule
from app.schemas.train_schedule import ScheduleResponse


router = APIRouter(
    prefix="/schedules",
    tags=["Schedules"],
)


# LIST AVAILABLE SCHEDULES
@router.get("/", response_model=list[ScheduleResponse])
def read_schedules(
    journey_date: date | None = None,
    route_id: int | None = None,
    db: Session = Depends(get_db),
):
    statement = select(TrainSchedule).where(
        TrainSchedule.status == "SCHEDULED"
    )

    if journey_date is not None:
        statement = statement.where(
            TrainSchedule.journey_date == journey_date
        )

    if route_id is not None:
        statement = statement.where(
            TrainSchedule.route_id == route_id
        )

    statement = statement.order_by(
        TrainSchedule.scheduled_departure_at
    )

    return db.scalars(statement).all()


# GET ONE BOOKABLE SCHEDULE
@router.get("/{schedule_id}", response_model=ScheduleResponse)
def read_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
):
    statement = select(TrainSchedule).where(
        TrainSchedule.id == schedule_id,
        TrainSchedule.status == "SCHEDULED",
    )

    schedule = db.scalar(statement)

    if schedule is None:
        raise HTTPException(
            status_code=404,
            detail="Bookable schedule not found.",
        )

    return schedule