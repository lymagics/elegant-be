from abc import ABC, abstractmethod

from plum import dispatch

from src.aop.awaited import awaited
from src.domain.user import User


class Users(ABC):
    @dispatch.abstract
    @abstractmethod
    @awaited
    async def user(self, id: str) -> User:
        pass

    @dispatch.abstract
    @abstractmethod
    @awaited
    async def user(self, email: str, password: str) -> User:  # noqa: F811
        pass

    @abstractmethod
    async def registration(self, username: str, email: str, password: str) -> User:
        pass
