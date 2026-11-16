from pydantic import BaseModel, ConfigDict, Field

class RouteStopCreate(BaseModel):
    route_id: int = Field(gt=0)
    station_id: int = Field(gt=0)
    stop_sequence: int = Field(gt=0)

class RouteStopUpdate(BaseModel):
    station_id: int = Field(gt=0)
    stop_sequence: int = Field(gt=0)

class RouteStopResponse(BaseModel):
    id: int
    route_id: int
    station_id: int
    stop_sequence: int

    model_config = ConfigDict(from_attributes=True)