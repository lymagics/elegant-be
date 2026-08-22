from hamcrest import assert_that, has_entries, has_entry, has_length

from src.domain.json_readable import JsonReadable
from src.domain.page import Page


class FakeJson(JsonReadable):
    def __init__(self, body: dict):
        self.body = body

    async def json(self) -> dict:
        return self.body


async def test_wraps_rows_and_meta_together():
    assert_that(
        await Page([FakeJson({"title": "Cold soup recipes"})], 41, 3, 10).json(),
        has_entry("meta", has_entries(total=41, page=3, limit=10)),
        "The page must carry pagination meta next to the data",
    )


async def test_keeps_every_given_row_in_data():
    assert_that(
        (
            await Page(
                [
                    FakeJson({"title": "One"}),
                    FakeJson({"title": "Two"}),
                    FakeJson({"title": "Three"}),
                ],
                3,
                1,
                20,
            ).json()
        )["data"],
        has_length(3),
        "The page must keep every row it was given",
    )
