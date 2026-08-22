from abc import ABC, abstractmethod


class JsonReadable(ABC):
    @abstractmethod
    async def json(self) -> dict:
        pass
