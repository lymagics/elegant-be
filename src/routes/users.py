from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.identity import Identity
from src.domain.json_readable import JsonReadable
from src.domain.user import PublicUser
from src.postgres.db import AsyncSQLAlchemyDb
from src.postgres.user import PgUser
from src.postgres.users import PgUsers
from src.routes.base import Bearer
from src.schemas.request.user import RegistrationSchema, UserPatchSchema
from src.schemas.response.user import UserSchema


class UserRoutes:
    def __init__(self, db: AsyncSQLAlchemyDb, bearer: Bearer):
        self.db = db
        self.bearer = bearer

    def router(self) -> APIRouter:
        router = APIRouter(tags=["Users"])

        @router.post("/users", status_code=201, response_model=UserSchema)
        async def registration(
            request: RegistrationSchema,
            db: AsyncSession = Depends(self.db.db),
        ) -> dict:
            user = await PgUsers(db).registration(
                request.username, request.email, request.password
            )
            return await user.json()

        @router.get("/users/me", response_model=UserSchema)
        async def current(
            identity: Identity = Depends(self.bearer),
            db: AsyncSession = Depends(self.db.db),
        ) -> dict:
            user = await PgUsers(db).user(identity.id())
            return await user.json()

        @router.patch("/users/me", response_model=UserSchema)
        async def renewal(
            request: UserPatchSchema,
            identity: Identity = Depends(self.bearer),
            db: AsyncSession = Depends(self.db.db),
        ) -> dict:
            user = PgUser(db, identity.id())
            await user.patch(request.model_dump(exclude_unset=True))
            return await user.json()

        @router.get("/users/{id}")
        async def profile(
            id: str,
            identity: Identity = Depends(self.bearer),
            db: AsyncSession = Depends(self.db.db),
        ) -> dict:
            user = await PgUsers(db).user(id)
            readable: JsonReadable = user
            if identity.id() != id:
                readable = PublicUser(user)
            return await readable.json()

        return router
