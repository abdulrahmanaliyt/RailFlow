
from pydantic import BaseModel, ConfigDict, Field


class StationCreate(BaseModel):
    station_code: str = Field(min_length=2, max_length=10)
    name: str = Field(min_length=2, max_length=100)
    city: str = Field(min_length=2, max_length=100)
    state: str = Field(min_length=2, max_length=100)


class StationUpdate(BaseModel):
    station_code: str = Field(min_length=2, max_length=10)
    name: str = Field(min_length=2, max_length=100)
    city: str = Field(min_length=2, max_length=100)
    state: str = Field(min_length=2, max_length=100)


class StationResponse(BaseModel):
    id: int
    station_code: str
    name: str
    city: str
    state: str

    model_config = ConfigDict(from_attributes=True)
