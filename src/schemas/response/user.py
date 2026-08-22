from pydantic import BaseModel


class UserSchema(BaseModel):
    id: str
    username: str
    email: str
    bio: str | None
    createdAt: str
    updatedAt: str
