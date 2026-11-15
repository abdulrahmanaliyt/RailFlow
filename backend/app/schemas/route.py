
from pydantic import BaseModel, ConfigDict, Field


class RouteCreate(BaseModel):
    train_id: int = Field(gt=0)
    route_name: str = Field(min_length=2, max_length=100)


class RouteUpdate(BaseModel):
    train_id: int = Field(gt=0)
    route_name: str = Field(min_length=2, max_length=100)


class RouteResponse(BaseModel):
    id: int
    train_id: int
    route_name: str

    model_config = ConfigDict(from_attributes=True)
