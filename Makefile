.PHONY: lint

lint:
	uv run ruff check api worker
	uv run ruff format --check api worker
	uv run mypy api
	uv run mypy worker
