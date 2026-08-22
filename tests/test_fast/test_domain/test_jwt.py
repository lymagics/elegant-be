import time

from hamcrest import (
    all_of,
    assert_that,
    calling,
    greater_than,
    has_entry,
    is_,
    less_than_or_equal_to,
    raises,
)

from src.domain.jwt import JwtClaims, JwtToken


async def test_carries_subject_through_round_trip():
    minted = JwtClaims({"sub": "writer-71ac", "exp": int(time.time()) + 120}).token(
        "kw9!x-secret-padded-to-thirty-two-bytes!"
    )
    assert_that(
        await JwtToken(minted.value(), "kw9!x-secret-padded-to-thirty-two-bytes!")
        .claims()
        .json(),
        has_entry("sub", "writer-71ac"),
        "Claims must survive the encode and decode round trip",
    )


def test_rejects_token_signed_with_other_secret():
    forged = JwtClaims({"sub": "intruder-3", "exp": int(time.time()) + 60}).token(
        "first-secret-padded-to-thirty-two-bytes"
    )
    assert_that(
        calling(
            JwtToken(forged.value(), "second-secret-padded-to-thirty-two-byte").claims
        ),
        raises(Exception, "not valid"),
        "A token signed with a different secret must be rejected",
    )


def test_rejects_expired_token_on_claims_reading():
    stale = JwtClaims({"sub": "sleeper-9", "exp": int(time.time()) - 3600}).token(
        "aged-secret-padded-to-thirty-two-bytes!!"
    )
    assert_that(
        calling(
            JwtToken(stale.value(), "aged-secret-padded-to-thirty-two-bytes!!").claims
        ),
        raises(Exception, "not valid"),
        "An expired token must not reveal its claims",
    )


def test_reports_expiration_of_stale_token():
    ancient = JwtClaims({"sub": "ghost-42", "exp": int(time.time()) - 7200}).token(
        "dusty-secret-padded-to-thirty-two-bytes!"
    )
    assert_that(
        JwtToken(ancient.value(), "dusty-secret-padded-to-thirty-two-bytes!").expired(),
        is_(True),
        "A token with a past expiry must report itself expired",
    )


def test_counts_remaining_lifetime_seconds():
    fresh = JwtClaims({"sub": "runner-5", "exp": int(time.time()) + 555}).token(
        "timer-secret-padded-to-thirty-two-bytes!"
    )
    assert_that(
        JwtToken(
            fresh.value(), "timer-secret-padded-to-thirty-two-bytes!"
        ).expires_in(),
        all_of(greater_than(540), less_than_or_equal_to(555)),
        "Remaining lifetime must be close to the minted expiry",
    )
