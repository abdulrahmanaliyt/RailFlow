from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_admin

from app.schemas.train_schedule import (
    ScheduleCreate,
    ScheduleUpdate,
    ScheduleResponse,
)

from app.services import train_schedule_service


router = APIRouter(
    prefix="/admin/schedules",
    tags=["Admin Schedules"],
    dependencies=[Depends(require_admin)],
)


# CREATE SCHEDULE
@router.post("/", response_model=ScheduleResponse, status_code=201)
def create_schedule_endpoint(
    data: ScheduleCreate,
    db: Session = Depends(get_db),
):
    try:
        return train_schedule_service.create_schedule(
            db,
            data,
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        )

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Duplicate or invalid schedule.",
        )


# GET ALL SCHEDULES
@router.get("/", response_model=list[ScheduleResponse])
def read_schedules(
    status: str | None = None,
    route_id: int | None = None,
    db: Session = Depends(get_db),
):
    return train_schedule_service.get_all_schedules(
        db,
        status=status,
        route_id=route_id,
    )


# GET SCHEDULE BY ID
@router.get("/{schedule_id}", response_model=ScheduleResponse)
def read_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
):
    schedule = train_schedule_service.get_schedule_by_id(
        db,
        schedule_id,
    )

    if schedule is None:
        raise HTTPException(
            status_code=404,
            detail="Schedule not found.",
        )

    return schedule


# UPDATE SCHEDULE
@router.patch("/{schedule_id}", response_model=ScheduleResponse)
def update_schedule_endpoint(
    schedule_id: int,
    data: ScheduleUpdate,
    db: Session = Depends(get_db),
):
    try:
        schedule = train_schedule_service.update_schedule(
            db,
            schedule_id,
            data,
        )

        if schedule is None:
            raise HTTPException(
                status_code=404,
                detail="Schedule not found.",
            )

        return schedule

    except ValueError as exc:
        db.rollback()

        raise HTTPException(
            status_code=422,
            detail=str(exc),
        )

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Schedule conflicts with an existing schedule.",
        )


# CANCEL SCHEDULE
@router.patch(
    "/{schedule_id}/cancel",
    response_model=ScheduleResponse,
)
def cancel_schedule_endpoint(
    schedule_id: int,
    db: Session = Depends(get_db),
):
    try:
        schedule = train_schedule_service.cancel_schedule(
            db,
            schedule_id,
        )

        if schedule is None:
            raise HTTPException(
                status_code=404,
                detail="Schedule not found.",
            )

        return schedule

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        )


# COMPLETE SCHEDULE
@router.patch(
    "/{schedule_id}/complete",
    response_model=ScheduleResponse,
)
def complete_schedule_endpoint(
    schedule_id: int,
    db: Session = Depends(get_db),
):
    try:
        schedule = train_schedule_service.complete_schedule(
            db,
            schedule_id,
        )

        if schedule is None:
            raise HTTPException(
                status_code=404,
                detail="Schedule not found.",
            )

        return schedule

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        )