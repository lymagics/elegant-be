# elegant-be

[![EO principles respected here](https://www.elegantobjects.org/badge.svg)](https://www.elegantobjects.org)

A blogging REST API built in the [Elegant Objects](https://www.elegantobjects.org)
style: immutable objects, interfaces everywhere, composition over
inheritance, no getters, no mocks.

## What it does

- **Users** — register, view and update your profile, look up other
  authors (their email stays private).
- **Tokens** — JWT sessions modeled as resources: log in with
  `POST /tokens`, refresh with `PATCH /tokens` via an `HttpOnly`
  cookie, log out with `DELETE /tokens`.
- **Posts** — full CRUD with drafts: unpublished posts are visible
  only to their author; guests browse published posts with
  pagination and author filters.

Interactive API docs are served at `/docs` once the API is running.

## Tech stack

| Layer      | Choice                                  |
|------------|-----------------------------------------|
| Language   | Python 3.12+, fully type-hinted         |
| Framework  | FastAPI                                 |
| Database   | PostgreSQL (SQLAlchemy async + asyncpg) |
| Migrations | Alembic                                 |
| Packaging  | uv                                      |

## Project layout

```
src/
  domain/    interfaces and pure domain objects (User, Post, JwtToken, ...)
  postgres/  PostgreSQL implementations of the domain interfaces
  routes/    FastAPI route classes (UserRoutes, TokenRoutes, PostRoutes)
  schemas/   pydantic request/response schemas
  app.py     Application class that assembles the FastAPI app
tests/
  test_fast/ unit tests with fakes (no external resources)
  test_deep/ integration tests against real PostgreSQL (Testcontainers)
```

## Quick start

Prerequisites: [uv](https://docs.astral.sh/uv/), Docker, make.

```
make install          # install dependencies
cp .env.example .env  # local configuration
make up               # start PostgreSQL (docker compose)
make migrate          # apply database migrations
make api              # serve http://localhost:8000
```

Stop the database with `make down`. Roll a migration back with
`make downgrade` (or `make downgrade ARGS=base` for all of them).

## Testing and quality

```
make unit   # fast unit tests, coverage gate at 90%
make e2e    # deep integration tests (needs Docker)
make lint   # black check + ruff + flake8
```

Run `make` alone to list every available command.

## Continuous integration

GitHub Actions runs `lint`, `unit` and `e2e` on every push to `main`
and every pull request — one workflow per job in `.github/workflows/`.

To run all workflows locally you need
[act](https://github.com/nektos/act), then:

```
make ci
```
