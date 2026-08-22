from datetime import UTC, datetime
from uuid import uuid4

from plum import dispatch
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.aop.awaited import awaited
from src.domain.password import Password
from src.domain.user import StoredUser, User
from src.domain.users import Users
from src.postgres.user import PgUser


class PgUsers(Users):
    def __init__(self, db: AsyncSession):
        self.db = db

    @dispatch
    @awaited
    async def user(self, id: str) -> User:
        result = await self.db.execute(
            text("SELECT * FROM users WHERE id::text = :id"), {"id": id}
        )
        row = result.mappings().one_or_none()
        if row is None:
            raise Exception(f"User {id} does not exist.")
        return StoredUser(PgUser(self.db, id), dict(row))

    @dispatch
    @awaited
    async def user(self, email: str, password: str) -> User:  # noqa: F811
        result = await self.db.execute(
            text("SELECT * FROM users WHERE email = :email"),
            {"email": email},
        )
        row = result.mappings().one_or_none()
        if row is None or not Password(password).matches(row["password"]):
            raise Exception("Wrong email or password.")
        return StoredUser(PgUser(self.db, str(row["id"])), dict(row))

    async def registration(self, username: str, email: str, password: str) -> User:
        now = datetime.now(UTC)
        id = str(uuid4())
        try:
            result = await self.db.execute(
                text(
                    "INSERT INTO users"
                    " (id, username, email, password, bio,"
                    " created_at, updated_at)"
                    " VALUES (:id, :username, :email, :password, NULL,"
                    " :created, :updated)"
                    " RETURNING *"
                ),
                {
                    "id": id,
                    "username": username,
                    "email": email,
                    "password": Password(password).hash(),
                    "created": now,
                    "updated": now,
                },
            )
        except IntegrityError as cause:
            raise self._conflict(cause, username, email) from cause
        return StoredUser(PgUser(self.db, id), dict(result.mappings().one()))

    def _conflict(self, cause: Exception, username: str, email: str) -> Exception:
        error = Exception(f"Registration failed: {cause}")
        if "users_email_key" in str(cause):
            error = Exception(f"Email {email} is already taken.")
        if "users_username_key" in str(cause):
            error = Exception(f"Username {username} is already taken.")
        return error
