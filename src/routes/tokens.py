import time

from fastapi import APIRouter, Cookie, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.identity import Identity
from src.domain.jwt import JwtClaims
from src.postgres.db import AsyncSQLAlchemyDb
from src.postgres.refreshes import PgRefreshes
from src.postgres.users import PgUsers
from src.routes.base import Bearer
from src.schemas.request.token import CredentialsSchema
from src.schemas.response.token import TokenSchema


class TokenRoutes:
    def __init__(self, db: AsyncSQLAlchemyDb, bearer: Bearer):
        self.db = db
        self.bearer = bearer

    def router(self) -> APIRouter:
        router = APIRouter(tags=["Tokens"])

        @router.post("/tokens", status_code=201, response_model=TokenSchema)
        async def grant(
            request: CredentialsSchema,
            answer: Response,
            db: AsyncSession = Depends(self.db.db),
        ) -> dict:
            user = await PgUsers(db).user(request.email, request.password)
            refresh = await PgRefreshes(db).grant(user.id())
            self._attach(answer, refresh.value())
            return self._body(user.id())

        @router.patch("/tokens", response_model=TokenSchema)
        async def renewal(
            answer: Response,
            token: str = Cookie(default="", alias="refreshToken"),
            db: AsyncSession = Depends(self.db.db),
        ) -> dict:
            if token == "":
                raise Exception("The refresh token cookie is missing.")
            refreshes = PgRefreshes(db)
            refresh = await refreshes.refresh(token)
            await refreshes.revoke(token)
            fresh = await refreshes.grant(refresh.owner())
            self._attach(answer, fresh.value())
            return self._body(refresh.owner())

        @router.delete("/tokens", status_code=204)
        async def revocation(
            identity: Identity = Depends(self.bearer),
            token: str = Cookie(default="", alias="refreshToken"),
            db: AsyncSession = Depends(self.db.db),
        ) -> Response:
            if token == "":
                raise Exception("The refresh token cookie is missing.")
            refreshes = PgRefreshes(db)
            await refreshes.refresh(token)
            await refreshes.revoke(token)
            answer = Response(status_code=204)
            answer.delete_cookie(
                "refreshToken",
                path="/v1/tokens",
                httponly=True,
                secure=True,
                samesite="strict",
            )
            return answer

        return router

    def _body(self, owner: str) -> dict:
        access = JwtClaims(
            {
                "sub": owner,
                "iat": int(time.time()),
                "exp": int(time.time()) + 900,
            }
        ).token(self.bearer.secret)
        return {
            "accessToken": access.value(),
            "expiresIn": access.expires_in(),
        }

    def _attach(self, answer: Response, value: str) -> None:
        answer.set_cookie(
            "refreshToken",
            value,
            max_age=604800,
            httponly=True,
            secure=True,
            samesite="strict",
            path="/v1/tokens",
        )
