class FakeResult:
    def __init__(self, rows: list[dict], count: int = 0):
        self.rows = rows
        self.rowcount = count

    def mappings(self) -> "FakeResult":
        return self

    def one_or_none(self) -> dict | None:
        return self.rows[0] if self.rows else None

    def one(self) -> dict:
        return self.rows[0]

    def all(self) -> list[dict]:
        return self.rows


class FakeSession:
    def __init__(self, results: list):
        self.results = list(results)
        self.queries: list[tuple[str, dict | None]] = []

    async def execute(self, statement, params: dict | None = None):
        self.queries.append((str(statement), params))
        result = self.results.pop(0)
        if isinstance(result, Exception):
            raise result
        return result
