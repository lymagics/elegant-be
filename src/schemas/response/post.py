from pydantic import BaseModel


class PostSchema(BaseModel):
    id: str
    authorId: str
    title: str
    content: str
    published: bool
    createdAt: str
    updatedAt: str


class MetaSchema(BaseModel):
    total: int
    page: int
    limit: int


class PageSchema(BaseModel):
    data: list[PostSchema]
    meta: MetaSchema
