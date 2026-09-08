import pytest
from elegant_jwt import ExpiringClaims, Hs256, JwtClaims
from hamcrest import assert_that, equal_to
from tanka import Abort, Empty, Get, Headers, Request

from src.routes.base import Bearer, SoftBearer


async def test_extracts_identity_from_valid_credentials():
    minted = ExpiringClaims(
        JwtClaims({"sub": "aabbccdd-1122-4334-8556-677889900aab"}),
        60,
    ).token(Hs256("gate-secret-1-padded-to-thirty-two-byte"))
    assert_that(
        (
            await Bearer("gate-secret-1-padded-to-thirty-two-byte").identity(
                Request(
                    Get(),
                    "/users/me",
                    Headers({"authorization": f"Bearer {minted.value()}"}),
                    Empty(),
                )
            )
        ).id(),
        equal_to("aabbccdd-1122-4334-8556-677889900aab"),
        "The bearer must extract the subject from a valid token",
    )


async def test_rejects_request_without_credentials():
    with pytest.raises(Abort, match="access token is missing"):
        await Bearer("gate-secret-2-padded-to-thirty-two-byte").identity(
            Request(Get(), "/users/me", Headers(), Empty())
        )


async def test_rejects_foreign_authorization_scheme():
    with pytest.raises(Abort, match="access token is missing"):
        await Bearer("gate-secret-6-padded-to-thirty-two-byte").identity(
            Request(
                Get(),
                "/posts",
                Headers({"authorization": "Basic bWFsbG9yeTpzZWNyZXQ="}),
                Empty(),
            )
        )


async def test_rejects_forged_credentials():
    intruded = ExpiringClaims(JwtClaims({"sub": "fraud-77"}), 45).token(
        Hs256("gate-secret-3-padded-to-thirty-two-byte")
    )
    with pytest.raises(Abort, match="not valid"):
        await Bearer("another-secret-padded-to-thirty-two-byte").identity(
            Request(
                Get(),
                "/users/me",
                Headers({"authorization": f"Bearer {intruded.value()}"}),
                Empty(),
            )
        )


async def test_rejects_expired_credentials():
    outdated = ExpiringClaims(JwtClaims({"sub": "relic-88"}), -7200).token(
        Hs256("gate-secret-5-padded-to-thirty-two-byte")
    )
    with pytest.raises(Abort, match="not valid"):
        await Bearer("gate-secret-5-padded-to-thirty-two-byte").identity(
            Request(
                Get(),
                "/users/me",
                Headers({"authorization": f"Bearer {outdated.value()}"}),
                Empty(),
            )
        )


async def test_lets_guest_pass_as_blank_identity():
    assert_that(
        (
            await SoftBearer(
                Bearer("gate-secret-4-padded-to-thirty-two-byte")
            ).identity(Request(Get(), "/posts/1a1a", Headers(), Empty()))
        ).id(),
        equal_to(""),
        "The soft bearer must turn a guest into a blank identity",
    )


async def test_hands_present_credentials_to_origin():
    minted = ExpiringClaims(JwtClaims({"sub": "reader-3c3c"}), 30).token(
        Hs256("gate-secret-7-padded-to-thirty-two-byte")
    )
    assert_that(
        (
            await SoftBearer(
                Bearer("gate-secret-7-padded-to-thirty-two-byte")
            ).identity(
                Request(
                    Get(),
                    "/posts/2b2b",
                    Headers({"authorization": f"Bearer {minted.value()}"}),
                    Empty(),
                )
            )
        ).id(),
        equal_to("reader-3c3c"),
        "The soft bearer must resolve present credentials through its origin",
    )
