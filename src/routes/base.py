from elegant_jwt import Hs256, JwtToken
from tanka import (
    Abort,
    Fallback,
    Identity,
    IdentitySource,
    Json,
    Log,
    Principal,
    Reply,
    Request,
    Response,
)
from ulid import ULID

from src.domain.envelope import Envelope


class Bearer(IdentitySource):
    def __init__(self, secret: str):
        self.secret = secret

    async def identity(self, request: Request) -> Identity:
        scheme, _, credentials = "".join(
            request.headers().values("authorization")[:1]
        ).partition(" ")
        if scheme.lower() != "bearer" or not credentials:
            raise Abort(401, "The access token is missing.")
        try:
            subject = JwtToken(credentials, Hs256(self.secret)).claims().json()["sub"]
        except Exception as error:
            raise Abort(401, str(error)) from error
        return Principal(subject)


class SoftBearer(IdentitySource):
    def __init__(self, origin: IdentitySource):
        self.origin = origin

    async def identity(self, request: Request) -> Identity:
        identity: Identity = Principal("")
        if request.headers().values("authorization"):
            identity = await self.origin.identity(request)
        return identity


class Recovery(Fallback):
    def __init__(self, log: Log):
        self.log = log

    async def response(self, request: Request, error: Abort) -> Reply:
        self.log.write(f"{request.target().path()} answered {error.status()}: {error}")
        return Response(
            error.status(),
            Json(await Envelope(error.status(), str(error), f"req_{ULID()}").json()),
        )
