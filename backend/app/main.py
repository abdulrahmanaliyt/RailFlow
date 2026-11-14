from fastapi import FastAPI

app = FastAPI(
    title="RailFlow API",
    description="Railway Reservation and Management System",
    version="0.1.0"
)


@app.get("/")
def home():
    return {
        "message": "Welcome to RailFlow API",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }