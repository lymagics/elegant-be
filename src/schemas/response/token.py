from pydantic import BaseModel


class TokenSchema(BaseModel):
    accessToken: str
    expiresIn: int
