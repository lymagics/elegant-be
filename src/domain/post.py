from abc import ABC, abstractmethod

from src.domain.json_readable import JsonReadable


class Post(ABC):
    @abstractmethod
    def id(self) -> str:
        pass

    @abstractmethod
    async def authored_by(self, author: str) -> bool:
        pass

    @abstractmethod
    async def published(self) -> bool:
        pass


class StoredPost(Post, JsonReadable):
    def __init__(self, origin: Post, row: dict):
        self.origin = origin
        self.row = row

    def id(self) -> str:
        return str(self.row["id"])

    async def authored_by(self, author: str) -> bool:
        return str(self.row["author"]) == author

    async def published(self) -> bool:
        return bool(self.row["published"])

    async def json(self) -> dict:
        return {
            "id": str(self.row["id"]),
            "authorId": str(self.row["author"]),
            "title": self.row["title"],
            "content": self.row["content"],
            "published": self.row["published"],
            "createdAt": self.row["created_at"].isoformat().replace("+00:00", "Z"),
            "updatedAt": self.row["updated_at"].isoformat().replace("+00:00", "Z"),
        }
