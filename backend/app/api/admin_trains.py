from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_admin

from app.schemas.train import (
    TrainCreate,
    TrainUpdate,
    TrainResponse,
)

from app.services.train_service import (
    create_train,
    get_all_trains,
    get_train_by_id,
    update_train,
    set_train_active,
)

router = APIRouter(
    prefix="/admin/trains",
    tags=["Admin Trains"],
    dependencies=[Depends(require_admin)],
)


# CREATE TRAIN
@router.post(
    "/",
    response_model=TrainResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_train_endpoint(
    train_data: TrainCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_train(db, train_data)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Train number already exists.",
        )


# GET ALL TRAINS INCLUDING INACTIVE
@router.get(
    "/",
    response_model=list[TrainResponse],
)
def read_all_trains(
    db: Session = Depends(get_db),
):
    return get_all_trains(
        db,
        include_inactive=True,
    )


# GET TRAIN BY ID
@router.get(
    "/{train_id}",
    response_model=TrainResponse,
)
def read_train(
    train_id: int,
    db: Session = Depends(get_db),
):
    train = get_train_by_id(db, train_id)

    if train is None:
        raise HTTPException(
            status_code=404,
            detail="Train not found.",
        )

    return train


# UPDATE TRAIN
@router.patch(
    "/{train_id}",
    response_model=TrainResponse,
)
def update_train_endpoint(
    train_id: int,
    train_data: TrainUpdate,
    db: Session = Depends(get_db),
):
    try:
        train = update_train(
            db,
            train_id,
            train_data,
        )

        if train is None:
            raise HTTPException(
                status_code=404,
                detail="Train not found.",
            )

        return train

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
            detail="Train number already exists.",
        )


# DEACTIVATE TRAIN
@router.patch(
    "/{train_id}/deactivate",
    response_model=TrainResponse,
)
def deactivate_train(
    train_id: int,
    db: Session = Depends(get_db),
):
    train = set_train_active(
        db,
        train_id,
        active=False,
    )

    if train is None:
        raise HTTPException(
            status_code=404,
            detail="Train not found.",
        )

    return train


# ACTIVATE TRAIN
@router.patch(
    "/{train_id}/activate",
    response_model=TrainResponse,
)
def activate_train(
    train_id: int,
    db: Session = Depends(get_db),
):
    train = set_train_active(
        db,
        train_id,
        active=True,
    )

    if train is None:
        raise HTTPException(
            status_code=404,
            detail="Train not found.",
        )

    return train