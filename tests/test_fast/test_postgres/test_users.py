from datetime import UTC, datetime

import pytest
from hamcrest import assert_that, equal_to, has_entry
from sqlalchemy.exc import IntegrityError

from src.domain.password import Password
from src.postgres.users import PgUsers
from tests.test_fast.fakes import FakeResult, FakeSession


async def test_builds_user_from_found_row():
    assert_that(
        await (
            await PgUsers(
                FakeSession(
                    [
                        FakeResult(
                            [
                                {
                                    "id": "11aa22bb-3344-4556-8778-99aabbccdd00",
                                    "username": "olga_hikes",
                                    "email": "olga@trails.example",
                                    "bio": None,
                                    "password": "irrelevant",
                                    "created_at": datetime(
                                        2026,
                                        2,
                                        2,
                                        12,
                                        0,
                                        tzinfo=UTC,
                                    ),
                                    "updated_at": datetime(
                                        2026,
                                        2,
                                        2,
                                        12,
                                        0,
                                        tzinfo=UTC,
                                    ),
                                }
                            ]
                        )
                    ]
                )
            ).user("11aa22bb-3344-4556-8778-99aabbccdd00")
        ).json(),
        has_entry("email", "olga@trails.example"),
        "A user found by id must expose its row as json",
    )


async def test_complains_about_unknown_id():
    with pytest.raises(Exception, match="does not exist"):
        await PgUsers(FakeSession([FakeResult([])])).user(
            "00000000-dead-4bee-8f00-000000000000"
        )


async def test_rejects_wrong_password():
    with pytest.raises(Exception, match="Wrong email or password"):
        await PgUsers(
            FakeSession(
                [
                    FakeResult(
                        [
                            {
                                "id": "ab12cd34-5678-4910-8111-213141516171",
                                "password": Password("real-53cret!").hash(),
                            }
                        ]
                    )
                ]
            )
        ).user("dana@mail.example", "guessed-badly")


async def test_accepts_valid_credentials():
    assert_that(
        (
            await PgUsers(
                FakeSession(
                    [
                        FakeResult(
                            [
                                {
                                    "id": "fe98dc76-ba54-4321-8fed-cba987654321",
                                    "password": Password("t0p-Secret-pass").hash(),
                                }
                            ]
                        )
                    ]
                )
            ).user("finn@sea.example", "t0p-Secret-pass")
        ).id(),
        equal_to("fe98dc76-ba54-4321-8fed-cba987654321"),
        "Valid credentials must resolve to the stored user",
    )


async def test_registers_and_returns_fresh_user():
    assert_that(
        await (
            await PgUsers(
                FakeSession(
                    [
                        FakeResult(
                            [
                                {
                                    "id": "0f1e2d3c-4b5a-4697-8879-9a0b1c2d3e4f",
                                    "username": "bram_codes",
                                    "email": "bram@dev.example",
                                    "bio": None,
                                    "created_at": datetime(
                                        2026,
                                        7,
                                        7,
                                        7,
                                        7,
                                        tzinfo=UTC,
                                    ),
                                    "updated_at": datetime(
                                        2026,
                                        7,
                                        7,
                                        7,
                                        7,
                                        tzinfo=UTC,
                                    ),
                                }
                            ]
                        )
                    ]
                )
            ).registration("bram_codes", "bram@dev.example", "l0ng-enough-pw")
        ).json(),
        has_entry("username", "bram_codes"),
        "Registration must return the freshly inserted user",
    )


async def test_translates_duplicate_email_into_conflict():
    with pytest.raises(Exception, match="already taken"):
        await PgUsers(
            FakeSession(
                [
                    IntegrityError(
                        "INSERT",
                        {},
                        Exception(
                            "duplicate key value violates unique"
                            ' constraint "users_email_key"'
                        ),
                    )
                ]
            )
        ).registration("dupe_dana", "dana@dup.example", "wh4tever-pw")


async def test_translates_duplicate_username_into_conflict():
    with pytest.raises(Exception, match="Username"):
        await PgUsers(
            FakeSession(
                [
                    IntegrityError(
                        "INSERT",
                        {},
                        Exception(
                            "duplicate key value violates unique"
                            ' constraint "users_username_key"'
                        ),
                    )
                ]
            )
        ).registration("taken_tara", "tara@fresh.example", "some-l0ng-pw!")
