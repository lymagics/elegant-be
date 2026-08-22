from datetime import UTC, datetime, timedelta

import pytest
from hamcrest import assert_that, equal_to

from src.postgres.refreshes import PgRefreshes
from tests.test_fast.fakes import FakeResult, FakeSession


async def test_grants_token_owned_by_given_user():
    assert_that(
        (
            await PgRefreshes(FakeSession([FakeResult([])])).grant(
                "c0ffee00-1234-4abc-8def-987654321000"
            )
        ).owner(),
        equal_to("c0ffee00-1234-4abc-8def-987654321000"),
        "A granted refresh token must belong to its user",
    )


async def test_rejects_unknown_token_value():
    with pytest.raises(Exception, match="refresh token is unknown"):
        await PgRefreshes(FakeSession([FakeResult([])])).refresh(
            "never-issued-value-51"
        )


async def test_rejects_token_past_its_expiry():
    with pytest.raises(Exception, match="refresh token has expired"):
        await PgRefreshes(
            FakeSession(
                [
                    FakeResult(
                        [
                            {
                                "value": "stale-token-92",
                                "owner": "abcdef01-2345-4678-89ab-cdef01234567",
                                "expires": datetime.now(UTC) - timedelta(minutes=1),
                            }
                        ]
                    )
                ]
            )
        ).refresh("stale-token-92")


async def test_returns_living_token_untouched():
    assert_that(
        (
            await PgRefreshes(
                FakeSession(
                    [
                        FakeResult(
                            [
                                {
                                    "value": "living-token-17",
                                    "owner": "0badf00d-9876-4543-8210-fedcba987654",
                                    "expires": datetime.now(UTC) + timedelta(days=3),
                                }
                            ]
                        )
                    ]
                )
            ).refresh("living-token-17")
        ).value(),
        equal_to("living-token-17"),
        "A living refresh token must come back with its value",
    )


async def test_sends_removal_of_revoked_value():
    session = FakeSession([FakeResult([])])
    await PgRefreshes(session).revoke("spent-token-33")
    assert_that(
        session.queries[0][1],
        equal_to({"value": "spent-token-33"}),
        "The revocation must pass the token value to the database",
    )
