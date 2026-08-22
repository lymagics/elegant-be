import pytest
from hamcrest import assert_that, equal_to, has_entry

from src.domain.envelope import Envelope


@pytest.mark.parametrize(
    ("message", "status"),
    [
        ("Wrong email or password.", 401),
        ("The access token is missing.", 401),
        ("The access token is not valid.", 401),
        ("The refresh token has expired.", 401),
        ("User 7c1d2e3f does not exist.", 404),
        ("Post 91aa22bb does not exist.", 404),
        ("Email zoe@taken.example is already taken.", 409),
        ("Username zoe_writes is already taken.", 409),
        ("You are not the author of this post.", 403),
        ("The post is not published.", 403),
        ("Title is blank.", 400),
    ],
)
def test_maps_message_to_http_status(message: str, status: int):
    assert_that(
        Envelope(Exception(message), "req_A1").status(),
        equal_to(status),
        f"'{message}' must map to HTTP {status}",
    )


@pytest.mark.parametrize(
    ("message", "code"),
    [
        ("Wrong email or password.", "INVALID_CREDENTIALS"),
        ("The access token is missing.", "UNAUTHORIZED"),
        ("The refresh token is unknown.", "INVALID_REFRESH_TOKEN"),
        ("User 55ff does not exist.", "USER_NOT_FOUND"),
        ("Post 66aa does not exist.", "POST_NOT_FOUND"),
        ("Email kai@dup.example is already taken.", "EMAIL_TAKEN"),
        ("Username kai_dup is already taken.", "USERNAME_TAKEN"),
        ("You are not the author of this post.", "FORBIDDEN"),
        ("Body field is broken somehow.", "VALIDATION_ERROR"),
    ],
)
async def test_maps_message_to_stable_code(message: str, code: str):
    assert_that(
        await Envelope(Exception(message), "req_B2").json(),
        has_entry("error", has_entry("code", code)),
        f"'{message}' must map to code {code}",
    )


async def test_keeps_original_message_in_body():
    assert_that(
        await Envelope(Exception("The post is not published."), "req_C3").json(),
        has_entry(
            "error",
            has_entry("message", "The post is not published."),
        ),
        "The envelope must keep the original error message",
    )
