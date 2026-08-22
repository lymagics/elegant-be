from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.page import Page
from src.domain.post import Post, StoredPost
from src.domain.posts import Posts
from src.postgres.post import PgPost


class PgPosts(Posts):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def post(self, id: str) -> Post:
        result = await self.db.execute(
            text("SELECT * FROM posts WHERE id::text = :id"), {"id": id}
        )
        row = result.mappings().one_or_none()
        if row is None:
            raise Exception(f"Post {id} does not exist.")
        return StoredPost(PgPost(self.db, id), dict(row))

    async def creation(
        self, author: str, title: str, content: str, published: bool
    ) -> Post:
        now = datetime.now(UTC)
        id = str(uuid4())
        result = await self.db.execute(
            text(
                "INSERT INTO posts"
                " (id, author, title, content, published,"
                " created_at, updated_at)"
                " VALUES (:id, :author, :title, :content, :published,"
                " :created, :updated)"
                " RETURNING *"
            ),
            {
                "id": id,
                "author": author,
                "title": title,
                "content": content,
                "published": published,
                "created": now,
                "updated": now,
            },
        )
        return StoredPost(PgPost(self.db, id), dict(result.mappings().one()))

    async def page(self, page: int, limit: int, author: str) -> Page:
        count = await self.db.execute(
            text(
                "SELECT COUNT(*) AS total FROM posts"
                " WHERE published = TRUE"
                " AND (:author = '' OR author::text = :author)"
            ),
            {"author": author},
        )
        rows = await self.db.execute(
            text(
                "SELECT * FROM posts"
                " WHERE published = TRUE"
                " AND (:author = '' OR author::text = :author)"
                " ORDER BY created_at DESC"
                " LIMIT :limit OFFSET :offset"
            ),
            {
                "author": author,
                "limit": limit,
                "offset": (page - 1) * limit,
            },
        )
        return Page(
            [
                StoredPost(PgPost(self.db, str(row["id"])), dict(row))
                for row in rows.mappings().all()
            ],
            count.mappings().one()["total"],
            page,
            limit,
        )

    async def remove(self, id: str) -> None:
        result = await self.db.execute(
            text("DELETE FROM posts WHERE id::text = :id"), {"id": id}
        )
        if result.rowcount == 0:
            raise Exception(f"Post {id} does not exist.")
