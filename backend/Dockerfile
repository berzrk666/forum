FROM python:3.13-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the project into the image
COPY . /app

# Disable development dependencies
ENV UV_NO_DEV=1

# Sync the project into a new environment, asserting the lockfile is up to date
WORKDIR /app

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "forum.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
