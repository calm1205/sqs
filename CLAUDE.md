# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Project Overview

Local SQS service using moto and Celery for async task processing.

## Tech Stack

- Python 3.14
- FastAPI (API service)
- Celery (task queue)
- moto_server (AWS SQS mock)
- boto3 / boto3-stubs
- celery-types
- uv (package manager)
- Docker

## Common Commands

```bash
# Start development server with hot reload
docker compose watch

# Run linter (ruff + mypy strict)
make lint

# Setup local environment
uv venv
uv sync
```

## Project Structure

```
├── api/
│   ├── Dockerfile
│   └── app/
│       └── main.py          # FastAPI application
├── worker/
│   ├── Dockerfile
│   └── app/
│       ├── celery.py        # Celery app configuration
│       └── tasks.py         # Celery tasks
├── sqs/
│   └── Dockerfile           # moto_server
├── pyproject.toml           # Project dependencies (root)
├── uv.lock
├── docker-compose.yml
├── Makefile
└── .env
```

## Architecture

- **api**: FastAPI service that creates Celery tasks
- **worker**: Celery worker that processes tasks from SQS
- **sqs**: moto_server providing AWS SQS mock

## Code Style

- Use ruff for linting and formatting
- Use mypy with `strict = true`
- Type annotations are required
- Use boto3-stubs for AWS type hints
- Use celery-types for Celery type hints
- Comments in Japanese

## Key Configurations

- Celery uses SQS as broker via `celery[sqs]`
- Dead Letter Queue with redrive policy (max 3 retries)
- Task acknowledgment after completion (`task_acks_late = True`)
