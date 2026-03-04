#!/bin/bash
set -e

uv run alembic upgrade head

if [ "$ENVIRONMENT" == "development" ]; then
  exec uv run uvicorn forum.main:app --host 0.0.0.0 --port 8000 --reload
else
  exec uv run uvicorn forum.main:app --host 0.0.0.0 --port 8000 --workers 4
fi
