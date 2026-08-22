from datetime import UTC, datetime

from hamcrest import assert_that, has_entry, is_

from src.domain.post import Post, StoredPost


class FakePost(Post):
    def id(self) -> str:
        return "stub-7"

    async def authored_by(self, author: str) -> bool:
        return False

    async def published(self) -> bool:
        return False


async def test_exposes_author_under_camel_case_key():
    assert_that(
        await StoredPost(
            FakePost(),
            {
                "id": "12ab34cd-5678-4901-a234-567890abcdef",
                "author": "98fe76dc-5432-4b10-9876-543210fedcba",
                "title": "Night trains of Moldova",
                "content": "The rails sing at 3am...",
                "published": True,
                "created_at": datetime(2026, 1, 15, 22, 45, tzinfo=UTC),
                "updated_at": datetime(2026, 1, 16, 6, 10, tzinfo=UTC),
            },
        ).json(),
        has_entry("authorId", "98fe76dc-5432-4b10-9876-543210fedcba"),
        "The stored post must expose the author under authorId",
    )


async def test_confirms_its_own_author():
    assert_that(
        await StoredPost(
            FakePost(),
            {"author": "0c1d2e3f-aaaa-4bbb-8ccc-dddd1111eeee"},
        ).authored_by("0c1d2e3f-aaaa-4bbb-8ccc-dddd1111eeee"),
        is_(True),
        "The post must confirm the author from its row",
    )


async def test_denies_foreign_author():
    assert_that(
        await StoredPost(
            FakePost(),
            {"author": "44445555-6666-4777-8888-99990000aaaa"},
        ).authored_by("deadbeef-1234-4321-abcd-ef9876543210"),
        is_(False),
        "The post must deny a stranger as its author",
    )


async def test_reports_unpublished_state():
    assert_that(
        await StoredPost(FakePost(), {"published": False}).published(),
        is_(False),
        "The post must report its unpublished state",
    )
