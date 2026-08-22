from datetime import UTC, datetime

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.json_patchable import JsonPatchable
from src.domain.json_readable import JsonReadable
from src.domain.post import Post, StoredPost


class PgPost(Post, JsonReadable, JsonPatchable):
    def __init__(self, db: AsyncSession, id: str):
        self.db = db
        self.key = id

    def id(self) -> str:
        return self.key

    async def authored_by(self, author: str) -> bool:
        result = await self.db.execute(
            text("SELECT author FROM posts WHERE id::text = :id"),
            {"id": self.key},
        )
        row = result.mappings().one_or_none()
        if row is None:
            raise Exception(f"Post {self.key} does not exist.")
        return str(row["author"]) == author

    async def published(self) -> bool:
        result = await self.db.execute(
            text("SELECT published FROM posts WHERE id::text = :id"),
            {"id": self.key},
        )
        row = result.mappings().one_or_none()
        if row is None:
            raise Exception(f"Post {self.key} does not exist.")
        return row["published"]

    async def json(self) -> dict:
        result = await self.db.execute(
            text("SELECT * FROM posts WHERE id::text = :id"),
            {"id": self.key},
        )
        row = result.mappings().one_or_none()
        if row is None:
            raise Exception(f"Post {self.key} does not exist.")
        return await StoredPost(self, dict(row)).json()

    async def patch(self, data: dict) -> None:
        fields = {
            name: data[name]
            for name in ("title", "content", "published")
            if name in data
        }
        sets = ", ".join(
            [f"{name} = :{name}" for name in fields] + ["updated_at = :updated"]
        )
        result = await self.db.execute(
            text(f"UPDATE posts SET {sets} WHERE id::text = :id"),
            {
                **fields,
                "updated": datetime.now(UTC),
                "id": self.key,
            },
        )
        if result.rowcount == 0:
            raise Exception(f"Post {self.key} does not exist.")
