from tanka import Abort, Endpoint, Json, Reply, Request, Response

from src.domain.json_readable import JsonReadable
from src.domain.user import PublicUser
from src.postgres.db import AsyncSQLAlchemyDb
from src.postgres.user import PgUser
from src.postgres.users import PgUsers


class Registration(Endpoint):
    def __init__(self, db: AsyncSQLAlchemyDb):
        self.db = db

    async def response(self, request: Request) -> Reply:
        body = await request.body().json()
        async with self.db.db() as db:
            try:
                user = await PgUsers(db).registration(
                    body["username"], body["email"], body["password"]
                )
            except Exception as error:
                raise Abort(409, str(error)) from error
            return Response(201, Json(await user.json()))


class OwnProfile(Endpoint):
    def __init__(self, db: AsyncSQLAlchemyDb):
        self.db = db

    async def response(self, request: Request) -> Reply:
        async with self.db.db() as db:
            try:
                user = await PgUsers(db).user(request.identity().id())
            except Exception as error:
                raise Abort(404, str(error)) from error
            return Response(Json(await user.json()))


class ProfileRenewal(Endpoint):
    def __init__(self, db: AsyncSQLAlchemyDb):
        self.db = db

    async def response(self, request: Request) -> Reply:
        body = await request.body().json()
        async with self.db.db() as db:
            user = PgUser(db, request.identity().id())
            try:
                await user.patch(body)
            except Exception as error:
                raise Abort(409, str(error)) from error
            return Response(Json(await user.json()))


class Profile(Endpoint):
    def __init__(self, db: AsyncSQLAlchemyDb):
        self.db = db

    async def response(self, request: Request) -> Reply:
        id = request.target().path().parameter("id")
        async with self.db.db() as db:
            try:
                user = await PgUsers(db).user(id)
            except Exception as error:
                raise Abort(404, str(error)) from error
            readable: JsonReadable = user
            if request.identity().id() != id:
                readable = PublicUser(user)
            return Response(Json(await readable.json()))
