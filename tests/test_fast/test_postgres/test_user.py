from datetime import UTC, datetime

import pytest
from hamcrest import assert_that, equal_to, has_entry
from sqlalchemy.exc import IntegrityError

from src.postgres.user import PgUser
from tests.test_fast.fakes import FakeResult, FakeSession


async def test_sends_patched_fields_to_database():
    session = FakeSession([FakeResult([], count=1)])
    await PgUser(session, "4d5e6f70-8192-4a3b-9c4d-5e6f70819202").patch(
        {"bio": "Sailing the Baltic."}
    )
    assert_that(
        session.queries[0][1],
        has_entry("bio", "Sailing the Baltic."),
        "The patch must pass the new bio to the database",
    )


async def test_complains_when_patching_missing_user():
    with pytest.raises(Exception, match="does not exist"):
        await PgUser(
            FakeSession([FakeResult([], count=0)]),
            "9a8b7c6d-5e4f-4321-8098-765432109876",
        ).patch({"username": "vanished_vera"})


def test_carries_its_key_as_id():
    assert_that(
        PgUser(FakeSession([]), "1a2b3c4d-5e6f-4708-8190-a1b2c3d4e5f6").id(),
        equal_to("1a2b3c4d-5e6f-4708-8190-a1b2c3d4e5f6"),
        "The postgres user must carry the key it was built with",
    )


async def test_reads_own_row_as_json():
    assert_that(
        await PgUser(
            FakeSession(
                [
                    FakeResult(
                        [
                            {
                                "id": "6f5e4d3c-2b1a-4908-8776-655443322110",
                                "username": "reading_rima",
                                "email": "rima@rows.example",
                                "bio": "Rows and columns.",
                                "created_at": datetime(2026, 3, 3, 3, 3, tzinfo=UTC),
                                "updated_at": datetime(2026, 3, 3, 3, 3, tzinfo=UTC),
                            }
                        ]
                    )
                ]
            ),
            "6f5e4d3c-2b1a-4908-8776-655443322110",
        ).json(),
        has_entry("email", "rima@rows.example"),
        "The postgres user must read its own row as json",
    )


async def test_complains_when_reading_ghost_row():
    with pytest.raises(Exception, match="does not exist"):
        await PgUser(
            FakeSession([FakeResult([])]),
            "0b1c2d3e-4f50-4617-8283-94a5b6c7d8e9",
        ).json()


async def test_translates_username_conflict_on_patch():
    with pytest.raises(Exception, match="already taken"):
        await PgUser(
            FakeSession(
                [
                    IntegrityError(
                        "UPDATE",
                        {},
                        Exception(
                            "duplicate key value violates unique"
                            ' constraint "users_username_key"'
                        ),
                    )
                ]
            ),
            "3e4f5a6b-7c8d-4e9f-8a0b-1c2d3e4f5a6b",
        ).patch({"username": "wanted_wanda"})
