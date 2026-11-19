from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.inventory import (
    CoachCreate,
    CoachUpdate,
    CoachResponse,
    SeatCreate,
    SeatUpdate,
    SeatResponse,
)
from app.services import inventory_service as service


router = APIRouter(tags=["Inventory"])


def handle_service_error(exc):
    if isinstance(exc, service.NotFoundError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    if isinstance(exc, service.ConflictError):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    raise exc


@router.post(
    "/trains/{train_id}/coaches",
    response_model=CoachResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a coach to a train",
    description="Creates a coach with a unique coach number for the selected train.",
)
def add_coach(
    train_id: int,
    payload: CoachCreate,
    db: Session = Depends(get_db),
):
    try:
        return service.create_coach(db, train_id, payload)
    except (service.NotFoundError, service.ConflictError) as exc:
        handle_service_error(exc)


@router.get(
    "/trains/{train_id}/coaches",
    response_model=list[CoachResponse],
    summary="List train coaches",
)
def list_train_coaches(
    train_id: int,
    db: Session = Depends(get_db),
):
    try:
        return service.get_train_coaches(db, train_id)
    except service.NotFoundError as exc:
        handle_service_error(exc)


@router.get(
    "/coaches/{coach_id}",
    response_model=CoachResponse,
    summary="Get coach details",
)
def get_coach(
    coach_id: int,
    db: Session = Depends(get_db),
):
    try:
        return service.get_coach(db, coach_id)
    except service.NotFoundError as exc:
        handle_service_error(exc)


@router.put(
    "/coaches/{coach_id}",
    response_model=CoachResponse,
    summary="Update coach details",
)
def update_coach(
    coach_id: int,
    payload: CoachUpdate,
    db: Session = Depends(get_db),
):
    try:
        return service.update_coach(db, coach_id, payload)
    except (service.NotFoundError, service.ConflictError) as exc:
        handle_service_error(exc)


@router.delete(
    "/coaches/{coach_id}",
    response_model=CoachResponse,
    summary="Deactivate a coach",
    description="Soft-deactivates the coach; it does not permanently delete the record.",
)
def delete_coach(
    coach_id: int,
    db: Session = Depends(get_db),
):
    try:
        return service.deactivate_coach(db, coach_id)
    except service.NotFoundError as exc:
        handle_service_error(exc)


@router.post(
    "/coaches/{coach_id}/seats",
    response_model=SeatResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a seat to a coach",
)
def add_seat(
    coach_id: int,
    payload: SeatCreate,
    db: Session = Depends(get_db),
):
    try:
        return service.create_seat(db, coach_id, payload)
    except (service.NotFoundError, service.ConflictError) as exc:
        handle_service_error(exc)


@router.get(
    "/coaches/{coach_id}/seats",
    response_model=list[SeatResponse],
    summary="List seats in a coach",
)
def list_coach_seats(
    coach_id: int,
    db: Session = Depends(get_db),
):
    try:
        return service.get_coach_seats(db, coach_id)
    except service.NotFoundError as exc:
        handle_service_error(exc)


@router.get(
    "/seats/{seat_id}",
    response_model=SeatResponse,
    summary="Get seat details",
)
def get_seat(
    seat_id: int,
    db: Session = Depends(get_db),
):
    try:
        return service.get_seat(db, seat_id)
    except service.NotFoundError as exc:
        handle_service_error(exc)


@router.put(
    "/seats/{seat_id}",
    response_model=SeatResponse,
    summary="Update seat details",
)
def update_seat(
    seat_id: int,
    payload: SeatUpdate,
    db: Session = Depends(get_db),
):
    try:
        return service.update_seat(db, seat_id, payload)
    except (service.NotFoundError, service.ConflictError) as exc:
        handle_service_error(exc)


@router.delete(
    "/seats/{seat_id}",
    response_model=SeatResponse,
    summary="Deactivate a seat",
    description="Soft-deactivates the seat; it does not permanently delete the record.",
)
def delete_seat(
    seat_id: int,
    db: Session = Depends(get_db),
):
    try:
        return service.deactivate_seat(db, seat_id)
    except service.NotFoundError as exc:
        handle_service_error(exc)