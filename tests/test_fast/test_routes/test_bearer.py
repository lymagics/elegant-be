import time

import pytest
from fastapi.security import HTTPAuthorizationCredentials
from hamcrest import assert_that, equal_to

from src.domain.jwt import JwtClaims
from src.routes.base import Bearer, SoftBearer


async def test_extracts_identity_from_valid_credentials():
    minted = JwtClaims(
        {
            "sub": "aabbccdd-1122-4334-8556-677889900aab",
            "exp": int(time.time()) + 60,
        }
    ).token("gate-secret-1-padded-to-thirty-two-byte")
    assert_that(
        (
            await Bearer("gate-secret-1-padded-to-thirty-two-byte")(
                HTTPAuthorizationCredentials(
                    scheme="Bearer", credentials=minted.value()
                )
            )
        ).id(),
        equal_to("aabbccdd-1122-4334-8556-677889900aab"),
        "The bearer must extract the subject from a valid token",
    )


async def test_rejects_request_without_credentials():
    with pytest.raises(Exception, match="access token is missing"):
        await Bearer("gate-secret-2-padded-to-thirty-two-byte")(None)


async def test_rejects_forged_credentials():
    intruded = JwtClaims({"sub": "fraud-77", "exp": int(time.time()) + 60}).token(
        "gate-secret-3-padded-to-thirty-two-byte"
    )
    with pytest.raises(Exception, match="not valid"):
        await Bearer("another-secret-padded-to-thirty-two-byte")(
            HTTPAuthorizationCredentials(scheme="Bearer", credentials=intruded.value())
        )


async def test_lets_guest_pass_as_blank_identity():
    assert_that(
        (
            await SoftBearer(Bearer("gate-secret-4-padded-to-thirty-two-byte"))(None)
        ).id(),
        equal_to(""),
        "The soft bearer must turn a guest into a blank identity",
    )
