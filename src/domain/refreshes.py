from abc import ABC, abstractmethod

from src.domain.refresh import Refresh


class Refreshes(ABC):
    @abstractmethod
    async def refresh(self, value: str) -> Refresh:
        pass

    @abstractmethod
    async def grant(self, owner: str) -> Refresh:
        pass

    @abstractmethod
    async def revoke(self, value: str) -> None:
        pass
