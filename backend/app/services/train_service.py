from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Train
from app.schemas.train import TrainCreate, TrainUpdate


def create_train(db: Session, train_data: TrainCreate):
    train = Train(
        train_number=train_data.train_number,
        train_name=train_data.train_name,
        is_active=True,
    )

    db.add(train)
    db.commit()
    db.refresh(train)

    return train


def get_all_trains(
    db: Session,
    include_inactive: bool = False,
):
    statement = select(Train).order_by(Train.id)

    if not include_inactive:
        statement = statement.where(Train.is_active.is_(True))

    return db.scalars(statement).all()


def get_train_by_id(
    db: Session,
    train_id: int,
    active_only: bool = False,
):
    statement = select(Train).where(Train.id == train_id)

    if active_only:
        statement = statement.where(Train.is_active.is_(True))

    return db.scalar(statement)


def update_train(
    db: Session,
    train_id: int,
    train_data: TrainUpdate,
):
    train = db.get(Train, train_id)

    if train is None:
        return None

    update_data = train_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if value is None:
            raise ValueError(f"{field} cannot be null.")

        setattr(train, field, value)

    db.commit()
    db.refresh(train)

    return train


def set_train_active(
    db: Session,
    train_id: int,
    active: bool,
):
    train = db.get(Train, train_id)

    if train is None:
        return None

    train.is_active = active

    db.commit()
    db.refresh(train)

    return train