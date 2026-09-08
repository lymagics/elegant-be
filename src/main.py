from os import environ

from src.app import ElegantBe
from src.postgres.db import AsyncSQLAlchemyDb
from src.routes.base import Bearer

app = (
    ElegantBe(
        AsyncSQLAlchemyDb(environ["DATABASE_URL"]),
        Bearer(environ["JWT_SECRET"]),
    )
    .app()
    .asgi()
)
