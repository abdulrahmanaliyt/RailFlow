# RailFlow

A full-stack Railway Reservation and Management System built with **React**, **FastAPI**, and **PostgreSQL**, featuring train search, seat availability, bookings, PNR generation, and sandbox payments.

## Tech Stack
- **Frontend:** React (Vite)
- **Backend:** FastAPI, SQLAlchemy, Alembic, Pydantic
- **Database:** PostgreSQL
- **Authentication:** JWT & Argon2 (`pwdlib`)

## Project Structure
```text
RailFlow/
├── backend/       # FastAPI application, models, schemas, migrations, and tests
├── frontend/      # React + Vite web application
├── docs/          # Requirements, ER diagrams, and API documentation
├── .gitignore
└── README.md