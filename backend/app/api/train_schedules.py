
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.train_schedule import (
    TrainScheduleCreate,
    TrainScheduleUpdate,
    TrainScheduleResponse,
)
from app.services import train_schedule_service


router = APIRouter(
    prefix="/schedules",
    tags=["Schedules"]
)


@router.post(
    "/",
    response_model=TrainScheduleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a train schedule",
    description="Creates a dated journey for an existing route.",
    response_description="The newly created train schedule."
)
def create_schedule(
    data: TrainScheduleCreate,
    db: Session = Depends(get_db)
):
    try:
        return train_schedule_service.create_schedule(db, data)

    except LookupError as exc:
        raise HTTPException(
        status_code=404,
        detail=str(exc)
    )
    
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="A schedule already exists for this route and departure time."
        )


@router.get(
    "/",
    response_model=list[TrainScheduleResponse],
    summary="Get all schedules",
    description="Returns all train schedules ordered by departure time.",
    response_description="List of train schedules."
)
def get_all_schedules(db: Session = Depends(get_db)):
    return train_schedule_service.get_all_schedules(db)


@router.get(
    "/route/{route_id}",
    response_model=list[TrainScheduleResponse],
    summary="List schedules for a route",
    description="Returns all schedules belonging to a specific train route.",
)
def get_schedules_by_route(
    route_id: int,
    db: Session = Depends(get_db)
):
    if not train_schedule_service.route_exists(db, route_id):
        raise HTTPException(
            status_code=404,
            detail="Train route not found"
        )
        
    schedules = train_schedule_service.get_schedules_by_route(
        db, route_id
    )

    return schedules


@router.get(
    "/{schedule_id}",
    response_model=TrainScheduleResponse,
    summary="Get a schedule",
    description="Finds a scheduled journey by its ID.",
    response_description="The requested train schedule."
)
def get_schedule(
    schedule_id: int,
    db: Session = Depends(get_db)
):
    schedule = train_schedule_service.get_schedule_by_id(
        db, schedule_id
    )

    if schedule is None:
        raise HTTPException(
            status_code=404,
            detail="Train schedule not found"
        )

    return schedule


@router.put(
    "/{schedule_id}",
    response_model=TrainScheduleResponse,
    summary="Update a schedule",
    description="Updates the date, departure, arrival and status of a schedule.",
    response_description="The updated train schedule."
)
def update_schedule(
    schedule_id: int,
    data: TrainScheduleUpdate,
    db: Session = Depends(get_db)
):
    try:
        schedule = train_schedule_service.update_schedule(
            db, schedule_id, data
        )

        if schedule is None:
            raise HTTPException(
                status_code=404,
                detail="Train schedule not found"
            )

        return schedule

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="The updated schedule conflicts with another schedule."
        )
