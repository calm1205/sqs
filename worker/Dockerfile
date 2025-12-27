FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv venv && uv sync --frozen --no-dev

COPY worker/celery_app.py worker/tasks.py ./
