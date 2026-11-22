from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.train import TrainResponse
from app.services.train_service import (
    get_all_trains,
    get_train_by_id,
)

router = APIRouter(
    prefix="/trains",
    tags=["Trains"],
)


# List all active trains
@router.get(
    "/",
    response_model=list[TrainResponse],
    summary="Get active trains",
    description="Retrieve all currently active trains.",
)
def read_trains(db: Session = Depends(get_db)):
    return get_all_trains(db, include_inactive=False)


# Get an active train by ID
@router.get(
    "/{train_id}",
    response_model=TrainResponse,
    summary="Get active train by ID",
    description="Retrieve an active train by its ID.",
)
def read_train(
    train_id: int,
    db: Session = Depends(get_db),
):
    train = get_train_by_id(db, train_id, active_only=True)

    if train is None:
        raise HTTPException(
            status_code=404,
            detail="Train not found.",
        )

    return train