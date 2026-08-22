from abc import ABC, abstractmethod

from src.domain.json_readable import JsonReadable


class User(ABC):
    @abstractmethod
    def id(self) -> str:
        pass


class StoredUser(User, JsonReadable):
    def __init__(self, origin: User, row: dict):
        self.origin = origin
        self.row = row

    def id(self) -> str:
        return str(self.row["id"])

    async def json(self) -> dict:
        return {
            "id": str(self.row["id"]),
            "username": self.row["username"],
            "email": self.row["email"],
            "bio": self.row["bio"],
            "createdAt": self.row["created_at"].isoformat().replace("+00:00", "Z"),
            "updatedAt": self.row["updated_at"].isoformat().replace("+00:00", "Z"),
        }


class PublicUser(JsonReadable):
    def __init__(self, origin: JsonReadable):
        self.origin = origin

    async def json(self) -> dict:
        full = await self.origin.json()
        return {name: full[name] for name in ("id", "username", "bio", "createdAt")}
