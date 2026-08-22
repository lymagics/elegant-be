from datetime import UTC, datetime

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.json_patchable import JsonPatchable
from src.domain.json_readable import JsonReadable
from src.domain.user import StoredUser, User


class PgUser(User, JsonReadable, JsonPatchable):
    def __init__(self, db: AsyncSession, id: str):
        self.db = db
        self.key = id

    def id(self) -> str:
        return self.key

    async def json(self) -> dict:
        result = await self.db.execute(
            text("SELECT * FROM users WHERE id::text = :id"),
            {"id": self.key},
        )
        row = result.mappings().one_or_none()
        if row is None:
            raise Exception(f"User {self.key} does not exist.")
        return await StoredUser(self, dict(row)).json()

    async def patch(self, data: dict) -> None:
        fields = {name: data[name] for name in ("username", "bio") if name in data}
        sets = ", ".join(
            [f"{name} = :{name}" for name in fields] + ["updated_at = :updated"]
        )
        try:
            result = await self.db.execute(
                text(f"UPDATE users SET {sets} WHERE id::text = :id"),
                {
                    **fields,
                    "updated": datetime.now(UTC),
                    "id": self.key,
                },
            )
        except IntegrityError as cause:
            raise Exception(
                f"Username {data.get('username')} is already taken."
            ) from cause
        if result.rowcount == 0:
            raise Exception(f"User {self.key} does not exist.")
