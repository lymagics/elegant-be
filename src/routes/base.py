import logging

from elegant_jwt import Hs256, JwtToken
from fastapi import Request, Security
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.responses import Response
from ulid import ULID

from src.domain.envelope import Envelope
from src.domain.identity import Identity


class Bearer:
    def __init__(self, secret: str):
        self.secret = secret

    async def __call__(
        self,
        grant: HTTPAuthorizationCredentials | None = Security(
            HTTPBearer(auto_error=False)
        ),
    ) -> Identity:
        if grant is None:
            raise Exception("The access token is missing.")
        claims = JwtToken(grant.credentials, Hs256(self.secret)).claims()
        return Identity(claims.json()["sub"])


class SoftBearer:
    def __init__(self, origin: Bearer):
        self.origin = origin

    async def __call__(
        self,
        grant: HTTPAuthorizationCredentials | None = Security(
            HTTPBearer(auto_error=False)
        ),
    ) -> Identity:
        identity = Identity("")
        if grant is not None:
            identity = await self.origin(grant)
        return identity


class Recovery(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, handler: RequestResponseEndpoint
    ) -> Response:
        try:
            answer = await handler(request)
        except Exception as error:
            envelope = Envelope(error, f"req_{ULID()}")
            logging.getLogger("app").warning(
                "%s answered %d: %s",
                request.url.path,
                envelope.status(),
                error,
            )
            answer = JSONResponse(await envelope.json(), status_code=envelope.status())
        return answer


async def invalid(request: Request, error: Exception) -> Response:
    envelope = Envelope(Exception(f"Request is not valid: {error}."), f"req_{ULID()}")
    return JSONResponse(await envelope.json(), status_code=envelope.status())
