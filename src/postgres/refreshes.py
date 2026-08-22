from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.refresh import Refresh, StoredRefresh
from src.domain.refreshes import Refreshes


class PgRefreshes(Refreshes):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def refresh(self, value: str) -> Refresh:
        result = await self.db.execute(
            text("SELECT * FROM refreshes WHERE value = :value"),
            {"value": value},
        )
        row = result.mappings().one_or_none()
        if row is None:
            raise Exception("The refresh token is unknown.")
        if row["expires"] < datetime.now(UTC):
            raise Exception("The refresh token has expired.")
        return StoredRefresh(dict(row))

    async def grant(self, owner: str) -> Refresh:
        row = {
            "value": str(uuid4()),
            "owner": owner,
            "expires": datetime.now(UTC) + timedelta(days=7),
        }
        await self.db.execute(
            text(
                "INSERT INTO refreshes (value, owner, expires)"
                " VALUES (:value, :owner, :expires)"
            ),
            row,
        )
        return StoredRefresh(row)

    async def revoke(self, value: str) -> None:
        await self.db.execute(
            text("DELETE FROM refreshes WHERE value = :value"),
            {"value": value},
        )
