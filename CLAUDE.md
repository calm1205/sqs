# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Project Overview

Local SQS service using moto and FastAPI for local development and testing.

## Tech Stack

- Python 3.14
- FastAPI
- moto (AWS mock)
- boto3
- uv (package manager)
- Docker

## Common Commands

```bash
# Start development server with hot reload
docker compose watch

# Run linter (ruff + mypy)
make lint

# Setup local environment
uv venv
uv sync
```

## Project Structure

```
├── app/
│   └── main.py          # FastAPI application with SQS endpoints
├── pyproject.toml       # Project dependencies
├── uv.lock              # Lock file
├── Dockerfile
├── docker-compose.yml
└── Makefile
```

## Code Style

- Use ruff for linting and formatting
- Use mypy for type checking
- Type annotations are required
- Use boto3-stubs for AWS type hints
