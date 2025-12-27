FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv venv && uv sync --frozen --no-dev

EXPOSE 5000

CMD ["uv", "run", "moto_server", "-H", "0.0.0.0", "-p", "5000"]
