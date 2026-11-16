
from fastapi import FastAPI

from app.api.stations import router as station_router
from app.api.trains import router as train_router
from app.api.routes import router as route_router
from app.api.route_stops import router as route_stop_router

tags_metadata = [
    {
        "name": "Stations",
        "description": (
            "Manage railway stations, including creation, "
            "retrieval, updating and deletion."
        ),
    },
    {
        "name": "Trains",
        "description": "Manage train information and services.",
    },
    {
        "name": "Routes",
        "description": "Manage train routes and station stops.",
    },
    {
        "name": "Schedules",
        "description": "Manage scheduled train journeys.",
    },
    {
        "name": "Bookings",
        "description": "Manage passenger reservations.",
    },
    {
        "name": "Authentication",
        "description": "User registration, login and authentication.",
    },
]

app = FastAPI(
    title="RailFlow — Railway Reservation System API",
    description="""
    ## About RailFlow

    RailFlow is a railway reservation backend built using
    FastAPI, SQLAlchemy and PostgreSQL.

    ### Core modules

    - User authentication
    - Station and train management
    - Route and schedule management
    - Seat availability
    - Ticket booking
    - Payment and cancellation
    """,
    version="1.0.0",
    openapi_tags=tags_metadata,
)

app.include_router(station_router)
app.include_router(train_router)
app.include_router(route_router)
app.include_router(route_stop_router)

@app.get(
    "/",
    tags=["General"],
    summary="API health welcome endpoint",
    description="Returns a welcome message confirming the API is accessible.",
)
def root():
    return {"message": "Welcome to RailFlow API"}
