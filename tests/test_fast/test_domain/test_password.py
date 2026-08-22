from hamcrest import assert_that, is_, starts_with

from src.domain.password import Password


def test_accepts_password_matching_its_own_hash():
    assert_that(
        Password("Qw3rty!$-long").matches(Password("Qw3rty!$-long").hash()),
        is_(True),
        "A password must match the hash made from itself",
    )


def test_rejects_wrong_password_against_foreign_hash():
    assert_that(
        Password("guess-111").matches(Password("truth-222!").hash()),
        is_(False),
        "A wrong password must not match a foreign hash",
    )


def test_builds_bcrypt_shaped_hash():
    assert_that(
        Password("s0mething-e1se").hash(),
        starts_with("$2b$"),
        "The hash must be in the bcrypt format",
    )
