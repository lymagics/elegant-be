import time

from elegant_jwt import ExpiringClaims, Hs256, JwtClaims
from tanka import (
    Abort,
    Cookie,
    CookiePath,
    Empty,
    Endpoint,
    ForgetCookie,
    HttpOnly,
    Json,
    Lifetime,
    Reply,
    Request,
    Response,
    SameSite,
    Secure,
    WithCookie,
)

from src.domain.json_readable import JsonReadable
from src.postgres.db import AsyncSQLAlchemyDb
from src.postgres.refreshes import PgRefreshes
from src.postgres.users import PgUsers
from src.routes.base import Bearer


class AccessToken(JsonReadable):
    def __init__(self, owner: str, secret: str):
        self.owner = owner
        self.secret = secret

    async def json(self) -> dict:
        access = ExpiringClaims(
            JwtClaims({"sub": self.owner, "iat": int(time.time())}),
            900,
        ).token(Hs256(self.secret))
        return {"accessToken": access.value(), "expiresIn": access.validity()}


class Grant(Endpoint):
    def __init__(self, db: AsyncSQLAlchemyDb, bearer: Bearer):
        self.db = db
        self.bearer = bearer

    async def response(self, request: Request) -> Reply:
        body = await request.body().json()
        async with self.db.db() as db:
            try:
                user = await PgUsers(db).user(body["email"], body["password"])
            except Exception as error:
                raise Abort(401, str(error)) from error
            refresh = await PgRefreshes(db).grant(user.id())
        return WithCookie(
            Response(
                201,
                Json(await AccessToken(user.id(), self.bearer.secret).json()),
            ),
            Cookie(
                "refreshToken",
                refresh.value(),
                HttpOnly(),
                Secure(),
                SameSite("Strict"),
                CookiePath("/v1/tokens"),
                Lifetime(604800),
            ),
        )


class TokenRenewal(Endpoint):
    def __init__(self, db: AsyncSQLAlchemyDb, bearer: Bearer):
        self.db = db
        self.bearer = bearer

    async def response(self, request: Request) -> Reply:
        try:
            token = request.cookies().cookie("refreshToken")
        except Exception as error:
            raise Abort(401, "The refresh token cookie is missing.") from error
        async with self.db.db() as db:
            refreshes = PgRefreshes(db)
            try:
                refresh = await refreshes.refresh(token)
            except Exception as error:
                raise Abort(401, str(error)) from error
            await refreshes.revoke(token)
            fresh = await refreshes.grant(refresh.owner())
        return WithCookie(
            Response(
                200,
                Json(await AccessToken(fresh.owner(), self.bearer.secret).json()),
            ),
            Cookie(
                "refreshToken",
                fresh.value(),
                HttpOnly(),
                Secure(),
                SameSite("Strict"),
                CookiePath("/v1/tokens"),
                Lifetime(604800),
            ),
        )


class Revocation(Endpoint):
    def __init__(self, db: AsyncSQLAlchemyDb):
        self.db = db

    async def response(self, request: Request) -> Reply:
        try:
            token = request.cookies().cookie("refreshToken")
        except Exception as error:
            raise Abort(401, "The refresh token cookie is missing.") from error
        async with self.db.db() as db:
            refreshes = PgRefreshes(db)
            try:
                await refreshes.refresh(token)
            except Exception as error:
                raise Abort(401, str(error)) from error
            await refreshes.revoke(token)
        return WithCookie(
            Response(204, Empty()),
            ForgetCookie(
                "refreshToken",
                HttpOnly(),
                Secure(),
                SameSite("Strict"),
                CookiePath("/v1/tokens"),
            ),
        )
