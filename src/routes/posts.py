from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.identity import Identity
from src.postgres.db import AsyncSQLAlchemyDb
from src.postgres.post import PgPost
from src.postgres.posts import PgPosts
from src.routes.base import Bearer, SoftBearer
from src.schemas.request.post import CreationSchema, PostPatchSchema
from src.schemas.response.post import PageSchema, PostSchema


class PostRoutes:
    def __init__(self, db: AsyncSQLAlchemyDb, bearer: Bearer):
        self.db = db
        self.bearer = bearer

    def router(self) -> APIRouter:
        router = APIRouter(tags=["Posts"])

        @router.post("/posts", status_code=201, response_model=PostSchema)
        async def creation(
            request: CreationSchema,
            identity: Identity = Depends(self.bearer),
            db: AsyncSession = Depends(self.db.db),
        ) -> dict:
            post = await PgPosts(db).creation(
                identity.id(),
                request.title,
                request.content,
                request.published,
            )
            return await post.json()

        @router.get("/posts", response_model=PageSchema)
        async def page(
            page: int = Query(default=1, ge=1),
            limit: int = Query(default=20, ge=1, le=100),
            author: str = Query(default="", alias="authorId"),
            db: AsyncSession = Depends(self.db.db),
        ) -> dict:
            sheet = await PgPosts(db).page(page, limit, author)
            return await sheet.json()

        @router.get("/posts/{id}", response_model=PostSchema)
        async def post(
            id: str,
            identity: Identity = Depends(SoftBearer(self.bearer)),
            db: AsyncSession = Depends(self.db.db),
        ) -> dict:
            record = await PgPosts(db).post(id)
            if not await record.published() and not await record.authored_by(
                identity.id()
            ):
                raise Exception("The post is not published.")
            return await record.json()

        @router.patch("/posts/{id}", response_model=PostSchema)
        async def renewal(
            id: str,
            request: PostPatchSchema,
            identity: Identity = Depends(self.bearer),
            db: AsyncSession = Depends(self.db.db),
        ) -> dict:
            record = PgPost(db, id)
            if not await record.authored_by(identity.id()):
                raise Exception("You are not the author of this post.")
            await record.patch(request.model_dump(exclude_unset=True))
            return await record.json()

        @router.delete("/posts/{id}", status_code=204)
        async def removal(
            id: str,
            identity: Identity = Depends(self.bearer),
            db: AsyncSession = Depends(self.db.db),
        ) -> Response:
            if not await PgPost(db, id).authored_by(identity.id()):
                raise Exception("You are not the author of this post.")
            await PgPosts(db).remove(id)
            return Response(status_code=204)

        return router
