#!/bin/bash
set -e

PORT="${PORT:-8000}"

uv run alembic upgrade head

if [ "$ENVIRONMENT" == "development" ]; then
  exec uv run uvicorn forum.main:app --host 0.0.0.0 --port "$PORT" --reload
else
  exec uv run uvicorn forum.main:app --host 0.0.0.0 --port "$PORT" --workers 4
fi
