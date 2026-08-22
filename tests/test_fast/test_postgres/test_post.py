from datetime import UTC, datetime

import pytest
from hamcrest import assert_that, equal_to, has_entry, is_

from src.postgres.post import PgPost
from tests.test_fast.fakes import FakeResult, FakeSession


async def test_confirms_author_from_selected_column():
    assert_that(
        await PgPost(
            FakeSession(
                [FakeResult([{"author": "aaaa1111-bbbb-4ccc-8ddd-eeee2222ffff"}])]
            ),
            "9999aaaa-8888-4bbb-8ccc-7777dddd6666",
        ).authored_by("aaaa1111-bbbb-4ccc-8ddd-eeee2222ffff"),
        is_(True),
        "The post must confirm authorship from the author column",
    )


async def test_reports_published_flag_from_database():
    assert_that(
        await PgPost(
            FakeSession([FakeResult([{"published": True}])]),
            "5555eeee-4444-4fff-8aaa-3333bbbb2222",
        ).published(),
        is_(True),
        "The post must report the published flag from the database",
    )


async def test_sends_patched_title_to_database():
    session = FakeSession([FakeResult([], count=1)])
    await PgPost(session, "7777cccc-6666-4ddd-8eee-5555ffff4444").patch(
        {"title": "Renamed at dawn"}
    )
    assert_that(
        session.queries[0][1],
        has_entry("title", "Renamed at dawn"),
        "The patch must pass the new title to the database",
    )


async def test_complains_when_checking_author_of_ghost():
    with pytest.raises(Exception, match="does not exist"):
        await PgPost(
            FakeSession([FakeResult([])]),
            "0e0e0e0e-1111-4222-8333-444455556666",
        ).authored_by("1b1b1b1b-2222-4333-8444-555566667777")


def test_carries_its_key_as_id():
    assert_that(
        PgPost(FakeSession([]), "8f7e6d5c-4b3a-4291-8807-766554433221").id(),
        equal_to("8f7e6d5c-4b3a-4291-8807-766554433221"),
        "The postgres post must carry the key it was built with",
    )


async def test_reads_own_row_as_json():
    assert_that(
        await PgPost(
            FakeSession(
                [
                    FakeResult(
                        [
                            {
                                "id": "2c3d4e5f-6a7b-4c8d-8e9f-0a1b2c3d4e5f",
                                "author": "b1c2d3e4-f5a6-4b7c-8d9e-0f1a2b3c4d5e",
                                "title": "Maps drawn from memory",
                                "content": "North was always wrong...",
                                "published": True,
                                "created_at": datetime(2026, 2, 20, 20, 2, tzinfo=UTC),
                                "updated_at": datetime(2026, 2, 21, 8, 15, tzinfo=UTC),
                            }
                        ]
                    )
                ]
            ),
            "2c3d4e5f-6a7b-4c8d-8e9f-0a1b2c3d4e5f",
        ).json(),
        has_entry("title", "Maps drawn from memory"),
        "The postgres post must read its own row as json",
    )


async def test_complains_when_checking_publication_of_ghost():
    with pytest.raises(Exception, match="does not exist"):
        await PgPost(
            FakeSession([FakeResult([])]),
            "4a5b6c7d-8e9f-4012-8345-6789abcdef01",
        ).published()


async def test_complains_when_patching_ghost_post():
    with pytest.raises(Exception, match="does not exist"):
        await PgPost(
            FakeSession([FakeResult([], count=0)]),
            "c9d8e7f6-a5b4-4c3d-8e2f-1a0b9c8d7e6f",
        ).patch({"content": "Shouting into the void."})
