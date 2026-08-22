from collections.abc import AsyncIterator, Iterator
from pathlib import Path

import pytest
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, text
from testcontainers.community.postgres import PostgresContainer

from alembic import command
from src.app import Application
from src.postgres.db import AsyncSQLAlchemyDb
from src.routes.base import Bearer
from src.routes.posts import PostRoutes
from src.routes.tokens import TokenRoutes
from src.routes.users import UserRoutes


@pytest.fixture(scope="session")
def postgres() -> Iterator[str]:
    with PostgresContainer("postgres:16-alpine") as container:
        yield container.get_connection_url()


@pytest.fixture
def migrated(postgres: str) -> str:
    engine = create_engine(postgres)
    with engine.begin() as connection:
        connection.execute(text("DROP SCHEMA public CASCADE"))
        connection.execute(text("CREATE SCHEMA public"))
    engine.dispose()
    config = Config()
    config.set_main_option(
        "script_location",
        str(Path(__file__).parents[2] / "alembic"),
    )
    config.set_main_option("sqlalchemy.url", postgres)
    command.upgrade(config, "head")
    return postgres


@pytest.fixture
async def client(
    migrated: str, request: pytest.FixtureRequest
) -> AsyncIterator[AsyncClient]:
    db = AsyncSQLAlchemyDb(migrated.replace("+psycopg2", "+asyncpg"))
    bearer = Bearer(f"deep-secret-{request.node.name}")
    transport = ASGITransport(
        app=Application(
            UserRoutes(db, bearer).router(),
            TokenRoutes(db, bearer).router(),
            PostRoutes(db, bearer).router(),
        ).app()
    )
    async with AsyncClient(transport=transport, base_url="https://stage") as browser:
        yield browser
    await db.engine.dispose()
