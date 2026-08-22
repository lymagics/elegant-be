from abc import ABC, abstractmethod

from src.domain.page import Page
from src.domain.post import Post


class Posts(ABC):
    @abstractmethod
    async def post(self, id: str) -> Post:
        pass

    @abstractmethod
    async def creation(
        self, author: str, title: str, content: str, published: bool
    ) -> Post:
        pass

    @abstractmethod
    async def page(self, page: int, limit: int, author: str) -> Page:
        pass

    @abstractmethod
    async def remove(self, id: str) -> None:
        pass
