
from app.db.database import SessionLocal
from app.models import Station

db = SessionLocal()

try:
    station = Station(
        station_code="TEST",
        name="Transaction Test Station",
        city="Test City",
        state="Test State"
    )

    db.add(station)

    # Send INSERT to PostgreSQL without committing
    db.flush()

    print("Station ID:", station.id)
    print("Station inserted inside transaction.")

    # Deliberately cancel the transaction
    db.rollback()

    print("Transaction rolled back.")

except Exception:
    db.rollback()
    raise

finally:
    db.close()
