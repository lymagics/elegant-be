from pydantic import BaseModel, Field


class CreationSchema(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    content: str = Field(min_length=1)
    published: bool = False


class PostPatchSchema(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    content: str | None = Field(default=None, min_length=1)
    published: bool | None = None
