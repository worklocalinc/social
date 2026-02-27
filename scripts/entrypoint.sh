#!/bin/bash
set -e

echo "Running migrations..."
alembic upgrade head

echo "Starting social service..."
exec uvicorn social.main:app --host 0.0.0.0 --port 8005
