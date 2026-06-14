#!/bin/bash
set -e

echo "Waiting for PostgreSQL to start..."
# Optional: could add a loop using pg_isready if needed, but usually restart: always is enough for simple setups

echo "Running migrations..."
alembic upgrade head

echo "Seeding the database..."
python -m app.db.seed

echo "Starting Uvicorn server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
