from os import environ

from src.app import Application
from src.postgres.db import AsyncSQLAlchemyDb
from src.routes.base import Bearer
from src.routes.posts import PostRoutes
from src.routes.tokens import TokenRoutes
from src.routes.users import UserRoutes

db = AsyncSQLAlchemyDb(environ["DATABASE_URL"])
bearer = Bearer(environ["JWT_SECRET"])

app = Application(
    UserRoutes(db, bearer).router(),
    TokenRoutes(db, bearer).router(),
    PostRoutes(db, bearer).router(),
).app()
