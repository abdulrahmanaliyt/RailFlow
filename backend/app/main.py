from fastapi import FastAPI

from app.api import availability, inventory, route_segments
from app.api.admin import router as admin_router
from app.api.admin_route_stops import router as admin_route_stops_router
from app.api.admin_routes import router as admin_route_router
from app.api.admin_stations import router as admin_stations_router
from app.api.admin_trains import router as admin_train_router
from app.api.auth import router as auth_router
from app.api.bookings import router as booking_router
from app.api.cancellations import router as cancellation_router
from app.api.payments import router as payment_router
from app.api.route_stops import router as route_stop_router
from app.api.routes import router as route_router
from app.api.search import router as search_router
from app.api.stations import router as station_router
from app.api.train_schedules import router as schedule_router
from app.api.trains import router as train_router

tags_metadata = [
    {
        "name": "General",
        "description": "Service health and welcome endpoints.",
    },
    {
        "name": "Authentication",
        "description": "User registration, login, and authentication.",
    },
    {
        "name": "Stations",
        "description": "Browse active railway stations.",
    },
    {
        "name": "Admin Stations",
        "description": (
            "Admin management of railway stations, including creation, "
            "updating, activation, and soft deactivation."
        ),
    },
    {
        "name": "Trains",
        "description": "Browse active railway trains.",
    },
    {
        "name": "Admin Trains",
        "description": "Admin-only train management and activation controls.",
    },
    {
        "name": "Routes",
        "description": "Manage train routes and station stops.",
    },
    {
        "name": "Route Stops",
        "description": "Manage stations and their sequence within train routes.",
    },
    {
        "name": "Admin Routes",
        "description": "Admin-only route creation, updates, and activation controls.",
    },
    {
        "name": "Admin Route Stops",
        "description": "Admin-only management of stations and sequence within routes.",
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
        "name": "Train Search",
        "description": "Search scheduled trains between two stations.",
    },
    {
        "name": "Inventory",
        "description": "Manage train coaches and their seats.",
    },
    {
        "name": "Route Segments",
        "description": "Generate and inspect consecutive segments of train routes.",
    },
    {
        "name": "Seat Availability",
        "description": "Check seat availability for a particular train journey.",
    },
]

app = FastAPI(
    title="RailFlow — Railway Reservation System API",
    description="""
## About RailFlow

RailFlow is a railway reservation backend built using
FastAPI, SQLAlchemy, and PostgreSQL.

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


@app.get(
    "/",
    tags=["General"],
    summary="API health welcome endpoint",
    description="Returns a welcome message confirming the API is accessible.",
)
def root() -> dict[str, str]:
    return {"message": "Welcome to RailFlow API"}


app.include_router(auth_router)
app.include_router(station_router)
app.include_router(admin_stations_router)
app.include_router(admin_train_router)
app.include_router(admin_route_router)
app.include_router(train_router)
app.include_router(route_router)
app.include_router(route_stop_router)
app.include_router(admin_route_stops_router)
app.include_router(schedule_router)
app.include_router(search_router)
app.include_router(inventory.router)
app.include_router(route_segments.router)
app.include_router(availability.router)
app.include_router(booking_router)
app.include_router(payment_router)
app.include_router(cancellation_router)
app.include_router(admin_router)