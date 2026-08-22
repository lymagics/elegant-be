from abc import ABC, abstractmethod


class Refresh(ABC):
    @abstractmethod
    def value(self) -> str:
        pass

    @abstractmethod
    def owner(self) -> str:
        pass


class StoredRefresh(Refresh):
    def __init__(self, row: dict):
        self.row = row

    def value(self) -> str:
        return self.row["value"]

    def owner(self) -> str:
        return str(self.row["owner"])
