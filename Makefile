.PHONY: lint lint-api lint-worker lint-sqs

lint: lint-api lint-worker lint-sqs

lint-api:
	cd api && uv run ruff check . && uv run ruff format --check . && uv run mypy .

lint-worker:
	cd worker && uv run ruff check . && uv run ruff format --check . && uv run mypy .

lint-sqs:
	cd sqs && uv run ruff check . && uv run ruff format --check . && uv run mypy .
