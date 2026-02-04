#!/bin/bash
set -e

echo "Waiting for postgres..."
while ! nc -z db 5432; do
  sleep 0.5
done
echo "Postgres has started."

echo "Applying migrations..."
poetry run alembic upgrade head

echo "Starting application..."
exec poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000