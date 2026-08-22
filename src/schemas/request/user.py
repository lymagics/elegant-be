from pydantic import BaseModel, EmailStr, Field


class RegistrationSchema(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)


class UserPatchSchema(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=30)
    bio: str | None = Field(default=None, max_length=500)
