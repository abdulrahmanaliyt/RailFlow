
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Train
from app.schemas.train import TrainCreate, TrainUpdate


def create_train(db: Session, train_data: TrainCreate):
    train = Train(**train_data.model_dump())

    db.add(train)
    db.commit()
    db.refresh(train)

    return train


def get_all_trains(db: Session):
    statement = select(Train).order_by(Train.id)
    return db.scalars(statement).all()


def get_train_by_id(db: Session, train_id: int):
    return db.get(Train, train_id)


def update_train(
    db: Session,
    train_id: int,
    train_data: TrainUpdate
):
    train = db.get(Train, train_id)

    if train is None:
        return None

    for field, value in train_data.model_dump().items():
        setattr(train, field, value)

    db.commit()
    db.refresh(train)

    return train


def delete_train(db: Session, train_id: int):
    train = db.get(Train, train_id)

    if train is None:
        return False

    db.delete(train)
    db.commit()

    return True
