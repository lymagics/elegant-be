from tanka import Abort, Empty, Endpoint, Json, Reply, Request, Response

from src.postgres.db import AsyncSQLAlchemyDb
from src.postgres.post import PgPost
from src.postgres.posts import PgPosts


class PostCreation(Endpoint):
    def __init__(self, db: AsyncSQLAlchemyDb):
        self.db = db

    async def response(self, request: Request) -> Reply:
        body = await request.body().json()
        async with self.db.db() as db:
            post = await PgPosts(db).creation(
                request.identity().id(),
                body["title"],
                body["content"],
                body.get("published", False),
            )
            return Response(201, Json(await post.json()))


class PostPage(Endpoint):
    def __init__(self, db: AsyncSQLAlchemyDb):
        self.db = db

    async def response(self, request: Request) -> Reply:
        query = request.target().query()
        async with self.db.db() as db:
            sheet = await PgPosts(db).page(
                int((query.values("page") or ["1"])[0]),
                int((query.values("limit") or ["20"])[0]),
                (query.values("authorId") or [""])[0],
            )
            return Response(Json(await sheet.json()))


class PostView(Endpoint):
    def __init__(self, db: AsyncSQLAlchemyDb):
        self.db = db

    async def response(self, request: Request) -> Reply:
        id = request.target().path().parameter("id")
        async with self.db.db() as db:
            try:
                record = await PgPosts(db).post(id)
            except Exception as error:
                raise Abort(404, str(error)) from error
            if not await record.published() and not await record.authored_by(
                request.identity().id()
            ):
                raise Abort(403, "The post is not published.")
            return Response(Json(await record.json()))


class PostRenewal(Endpoint):
    def __init__(self, db: AsyncSQLAlchemyDb):
        self.db = db

    async def response(self, request: Request) -> Reply:
        body = await request.body().json()
        async with self.db.db() as db:
            record = PgPost(db, request.target().path().parameter("id"))
            try:
                authorship = await record.authored_by(request.identity().id())
            except Exception as error:
                raise Abort(404, str(error)) from error
            if not authorship:
                raise Abort(403, "You are not the author of this post.")
            await record.patch(body)
            return Response(Json(await record.json()))


class PostRemoval(Endpoint):
    def __init__(self, db: AsyncSQLAlchemyDb):
        self.db = db

    async def response(self, request: Request) -> Reply:
        id = request.target().path().parameter("id")
        async with self.db.db() as db:
            try:
                authorship = await PgPost(db, id).authored_by(request.identity().id())
            except Exception as error:
                raise Abort(404, str(error)) from error
            if not authorship:
                raise Abort(403, "You are not the author of this post.")
            await PgPosts(db).remove(id)
        return Response(204, Empty())
