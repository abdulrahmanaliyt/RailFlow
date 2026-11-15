
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.train import (
    TrainCreate,
    TrainUpdate,
    TrainResponse
)
from app.services.train_service import (
    create_train,
    get_all_trains,
    get_train_by_id,
    update_train,
    delete_train
)

router = APIRouter(
    prefix="/trains",
    tags=["Trains"]
)


@router.post(
    "/",
    response_model=TrainResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new train",
    description="Register a new train using its unique train number."
)
def create_train_endpoint(
    train_data: TrainCreate,
    db: Session = Depends(get_db)
):
    try:
        return create_train(db, train_data)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Train number already exists or violates a database constraint."
        )


@router.get(
    "/",
    response_model=list[TrainResponse],
    summary="Get all trains",
    description="Retrieve all registered trains."
)
def read_trains(db: Session = Depends(get_db)):
    return get_all_trains(db)


@router.get(
    "/{train_id}",
    response_model=TrainResponse,
    summary="Get train by ID"
)
def read_train(
    train_id: int,
    db: Session = Depends(get_db)
):
    train = get_train_by_id(db, train_id)

    if train is None:
        raise HTTPException(
            status_code=404,
            detail="Train not found."
        )

    return train


@router.put(
    "/{train_id}",
    response_model=TrainResponse,
    summary="Update train information"
)
def update_train_endpoint(
    train_id: int,
    train_data: TrainUpdate,
    db: Session = Depends(get_db)
):
    try:
        train = update_train(db, train_id, train_data)

        if train is None:
            raise HTTPException(
                status_code=404,
                detail="Train not found."
            )

        return train

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Train update violates a database constraint."
        )


@router.delete(
    "/{train_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a train"
)
def remove_train(
    train_id: int,
    db: Session = Depends(get_db)
):
    try:
        deleted = delete_train(db, train_id)

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Train not found."
            )

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Cannot delete this train because it is referenced by another record."
        )
