from elegant_jwt import Hs256, JwtToken
from hamcrest import assert_that, has_entry

from src.routes.tokens import AccessToken


async def test_signs_owner_into_subject():
    minted = await AccessToken(
        "b4b4c5c5-6d6d-4e7e-8f8f-909091919292",
        "mint-secret-1-padded-to-thirty-two-bytes",
    ).json()
    assert_that(
        JwtToken(
            minted["accessToken"],
            Hs256("mint-secret-1-padded-to-thirty-two-bytes"),
        )
        .claims()
        .json(),
        has_entry("sub", "b4b4c5c5-6d6d-4e7e-8f8f-909091919292"),
        "The access token must carry its owner as the subject",
    )


async def test_expires_in_fifteen_minutes():
    assert_that(
        await AccessToken(
            "d1d1e2e2-3f3f-4a4a-8b8b-5c5c6d6d7e7e",
            "mint-secret-2-padded-to-thirty-two-bytes",
        ).json(),
        has_entry("expiresIn", 900),
        "The access token must announce a fifteen minute validity",
    )
