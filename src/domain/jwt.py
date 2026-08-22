import time

import jwt as pyjwt

from src.domain.json_readable import JsonReadable


class JwtToken:
    def __init__(self, value: str, secret: str):
        self.raw = value
        self.secret = secret

    def claims(self) -> "JwtClaims":
        try:
            return JwtClaims(pyjwt.decode(self.raw, self.secret, algorithms=["HS256"]))
        except pyjwt.PyJWTError as cause:
            raise Exception("The access token is not valid.") from cause

    def expired(self) -> bool:
        return self.expires_in() == 0

    def expires_in(self) -> int:
        payload = pyjwt.decode(
            self.raw,
            self.secret,
            algorithms=["HS256"],
            options={"verify_exp": False},
        )
        return max(0, int(payload["exp"]) - int(time.time()))

    def value(self) -> str:
        return self.raw


class JwtClaims(JsonReadable):
    def __init__(self, payload: dict):
        self.payload = payload

    def token(self, secret: str) -> JwtToken:
        return JwtToken(pyjwt.encode(self.payload, secret, algorithm="HS256"), secret)

    async def json(self) -> dict:
        return dict(self.payload)
