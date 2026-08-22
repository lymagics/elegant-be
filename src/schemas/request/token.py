from pydantic import BaseModel, EmailStr, Field


class CredentialsSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)
