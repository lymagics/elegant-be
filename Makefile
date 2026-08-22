.DEFAULT_GOAL := help
.PHONY: help install up down api migrate downgrade migrate-history unit e2e black flake8 ruff lint ci

help:
	@echo "Available commands:"
	@echo "  make install          Install deps (uv)"
	@echo "  make up               Start local Postgres (docker compose)"
	@echo "  make down             Stop local Postgres"
	@echo "  make api              Run the API (http://localhost:8000)"
	@echo "  make migrate          Migrate the database to head"
	@echo "  make downgrade        Downgrade one revision (target via ARGS=)"
	@echo "  make migrate-history  Show revision history (extra args via ARGS=)"
	@echo "  make unit             Run fast (unit) tests with coverage"
	@echo "  make e2e              Run deep (integration) tests - needs Docker"
	@echo "  make black            Format code with black"
	@echo "  make flake8           Run flake8"
	@echo "  make ruff             Run ruff with autofix"
	@echo "  make lint             Black check + ruff + flake8"
	@echo "  make ci               Run GitHub Actions workflows locally (act)"

install:
	uv sync

up:
	docker compose up -d --wait

down:
	docker compose down

api:
	uv run --env-file .env uvicorn src.main:app --port 8000

migrate:
	uv run --env-file .env alembic upgrade head

downgrade:
	uv run --env-file .env alembic downgrade $(or $(ARGS),-1)

migrate-history:
	uv run --env-file .env alembic history $(ARGS)

unit:
	uv run pytest tests/test_fast --cov=src --cov-report=term-missing --cov-fail-under=90

e2e:
	uv run pytest tests/test_deep

black:
	uv run black src tests

flake8:
	uv run flake8 src tests

ruff:
	uv run ruff check --fix src tests

lint:
	uv run black --check src tests && uv run ruff check src tests && uv run flake8 src tests

ci:
	act push -P ubuntu-latest=catthehacker/ubuntu:act-latest --env TESTCONTAINERS_HOST_OVERRIDE=host.docker.internal
