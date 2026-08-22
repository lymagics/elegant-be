from abc import ABC, abstractmethod


class JsonPatchable(ABC):
    @abstractmethod
    async def patch(self, data: dict) -> None:
        pass
