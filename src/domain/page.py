from src.domain.json_readable import JsonReadable


class Page(JsonReadable):
    def __init__(self, posts: list[JsonReadable], total: int, page: int, limit: int):
        self.posts = posts
        self.total = total
        self.page = page
        self.limit = limit

    async def json(self) -> dict:
        return {
            "data": [await post.json() for post in self.posts],
            "meta": {
                "total": self.total,
                "page": self.page,
                "limit": self.limit,
            },
        }
