from sqlalchemy import select
from app.db.database import SessionLocal
from app.models import Station, Train

db = SessionLocal()

try:
    # 1. CREATE — Add a new Station
    new_station = Station(
        station_code="AGC", 
        name="Agra Cantt", 
        city="Agra", 
        state="Uttar Pradesh"
    )
    db.add(new_station)
    db.commit()
    db.refresh(new_station)
    print("Station created successfully!")
    print("ID:", new_station.id)
    print("Name:", new_station.name)

    # 2. READ — Retrieve all stations
    statement = select(Station)
    stations = db.scalars(statement).all()
    print("\n--- All Stations in Database ---")
    for s in stations:
        print(s.id, s.station_code, s.name, s.city)

    # 3. READ — Retrieve one station by ID
    station_by_id = db.get(Station, new_station.id)
    if station_by_id:
        print(f"\nFetched single station by ID {station_by_id.id}: {station_by_id.name}")

    # 4. UPDATE — Modify an existing station's city
    if station_by_id:
        station_by_id.city = "Agra City"
        db.commit()
        db.refresh(station_by_id)
        print(f"Station updated! New city: {station_by_id.city}")

    # 5. CREATE — Add a Train record
    new_train = Train(
        train_number="12951",
        train_name="Rajdhani Express",
        is_active=True
    )
    db.add(new_train)
    db.commit()
    db.refresh(new_train)
    print(f"\nTrain created: {new_train.train_name} ({new_train.train_number})")

    # READ — Retrieve all trains
    trains = db.scalars(select(Train)).all()
    print("--- All Trains in Database ---")
    for t in trains:
        print(t.id, t.train_number, t.train_name, t.is_active)

except Exception:
    db.rollback()
    raise
finally:
    db.close()
    print("\nDatabase session closed.")