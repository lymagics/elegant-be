from datetime import UTC, datetime

from hamcrest import assert_that, equal_to, has_entries, has_key, is_not

from src.domain.user import PublicUser, StoredUser, User


class FakeUser(User):
    def id(self) -> str:
        return "seed-1"


async def test_builds_camel_case_json_from_row():
    assert_that(
        await StoredUser(
            FakeUser(),
            {
                "id": "aa11bb22-0000-4111-8222-333344445555",
                "username": "marta_reads",
                "email": "marta@writers.example",
                "bio": None,
                "created_at": datetime(2026, 3, 9, 8, 30, tzinfo=UTC),
                "updated_at": datetime(2026, 3, 9, 8, 30, tzinfo=UTC),
            },
        ).json(),
        has_entries(
            username="marta_reads",
            createdAt="2026-03-09T08:30:00Z",
        ),
        "The stored user must expose camelCase fields with Z timestamps",
    )


async def test_hides_email_in_public_profile():
    assert_that(
        await PublicUser(
            StoredUser(
                FakeUser(),
                {
                    "id": "77aa66bb-1111-4222-9333-aaaabbbbcccc",
                    "username": "silent_ivo",
                    "email": "ivo@hidden.example",
                    "bio": "Privacy first.",
                    "created_at": datetime(2025, 12, 1, 17, 5, tzinfo=UTC),
                    "updated_at": datetime(2025, 12, 2, 9, 0, tzinfo=UTC),
                },
            )
        ).json(),
        is_not(has_key("email")),
        "The public profile must not leak the email address",
    )


def test_takes_id_from_row_not_origin():
    assert_that(
        StoredUser(
            FakeUser(),
            {"id": "f0e1d2c3-9999-4888-b777-666655554444"},
        ).id(),
        equal_to("f0e1d2c3-9999-4888-b777-666655554444"),
        "The stored user id must come from the row",
    )
