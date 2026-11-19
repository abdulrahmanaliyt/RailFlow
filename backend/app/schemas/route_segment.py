from pydantic import BaseModel, ConfigDict


class RouteSegmentResponse(BaseModel):
    id: int
    route_id: int
    from_route_stop_id: int
    to_route_stop_id: int
    segment_sequence: int

    model_config = ConfigDict(from_attributes=True)