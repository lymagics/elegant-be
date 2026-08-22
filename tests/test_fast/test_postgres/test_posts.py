from datetime import UTC, datetime

import pytest
from hamcrest import assert_that, has_entry

from src.postgres.posts import PgPosts
from tests.test_fast.fakes import FakeResult, FakeSession


async def test_complains_about_unknown_post():
    with pytest.raises(Exception, match="does not exist"):
        await PgPosts(FakeSession([FakeResult([])])).post(
            "0000aaaa-bbbb-4ccc-8ddd-eeee1111ffff"
        )


async def test_creates_post_with_given_author():
    assert_that(
        await (
            await PgPosts(
                FakeSession(
                    [
                        FakeResult(
                            [
                                {
                                    "id": "5a6b7c8d-9e0f-4a1b-8c2d-3e4f5a6b7c8d",
                                    "author": "1f2e3d4c-5b6a-4798-8081-92a3b4c5d6e7",
                                    "title": "Bread that failed",
                                    "content": "Third time the yeast...",
                                    "published": False,
                                    "created_at": datetime(
                                        2026,
                                        4,
                                        1,
                                        6,
                                        0,
                                        tzinfo=UTC,
                                    ),
                                    "updated_at": datetime(
                                        2026,
                                        4,
                                        1,
                                        6,
                                        0,
                                        tzinfo=UTC,
                                    ),
                                }
                            ]
                        )
                    ]
                )
            ).creation(
                "1f2e3d4c-5b6a-4798-8081-92a3b4c5d6e7",
                "Bread that failed",
                "Third time the yeast...",
                False,
            )
        ).json(),
        has_entry("authorId", "1f2e3d4c-5b6a-4798-8081-92a3b4c5d6e7"),
        "The created post must carry the author it was given",
    )


async def test_pages_posts_with_meta_total():
    assert_that(
        await (
            await PgPosts(
                FakeSession(
                    [
                        FakeResult([{"total": 23}]),
                        FakeResult([]),
                    ]
                )
            ).page(2, 5, "")
        ).json(),
        has_entry("meta", has_entry("total", 23)),
        "The page must report the database total in meta",
    )


async def test_refuses_to_remove_ghost_post():
    with pytest.raises(Exception, match="does not exist"):
        await PgPosts(FakeSession([FakeResult([], count=0)])).remove(
            "12345678-9abc-4def-8123-456789abcdef"
        )


async def test_builds_post_from_found_row():
    assert_that(
        await (
            await PgPosts(
                FakeSession(
                    [
                        FakeResult(
                            [
                                {
                                    "id": "e1f2a3b4-c5d6-4e7f-8091-a2b3c4d5e6f7",
                                    "author": "9e8d7c6b-5a49-4382-8716-05f4e3d2c1b0",
                                    "title": "Tram lines at dusk",
                                    "content": "Sparks over the junction...",
                                    "published": True,
                                    "created_at": datetime(
                                        2026, 5, 12, 19, 40, tzinfo=UTC
                                    ),
                                    "updated_at": datetime(
                                        2026, 5, 12, 19, 40, tzinfo=UTC
                                    ),
                                }
                            ]
                        )
                    ]
                )
            ).post("e1f2a3b4-c5d6-4e7f-8091-a2b3c4d5e6f7")
        ).json(),
        has_entry("title", "Tram lines at dusk"),
        "A post found by id must expose its row as json",
    )
