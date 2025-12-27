.PHONY: lint

lint:
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy .
