
from pydantic import BaseModel, ConfigDict, Field


class TrainCreate(BaseModel):
    train_number: str = Field(min_length=1, max_length=20)
    train_name: str = Field(min_length=2, max_length=150)
    is_active: bool = True


class TrainUpdate(BaseModel):
    train_number: str = Field(min_length=1, max_length=20)
    train_name: str = Field(min_length=2, max_length=150)
    is_active: bool


class TrainResponse(BaseModel):
    id: int
    train_number: str
    train_name: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
