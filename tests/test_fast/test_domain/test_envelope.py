import pytest
from hamcrest import assert_that, has_entry

from src.domain.envelope import Envelope


@pytest.mark.parametrize(
    ("status", "message", "code"),
    [
        (401, "Wrong email or password.", "INVALID_CREDENTIALS"),
        (401, "The refresh token is unknown.", "INVALID_REFRESH_TOKEN"),
        (401, "The refresh token cookie is missing.", "INVALID_REFRESH_TOKEN"),
        (404, "User 55ff does not exist.", "USER_NOT_FOUND"),
        (404, "Post 66aa does not exist.", "POST_NOT_FOUND"),
        (409, "Email kai@dup.example is already taken.", "EMAIL_TAKEN"),
        (409, "Username kai_dup is already taken.", "USERNAME_TAKEN"),
        (401, "The access token is missing.", "UNAUTHORIZED"),
        (403, "You are not the author of this post.", "FORBIDDEN"),
        (404, "No route matches DELETE /v9/things", "NOT_FOUND"),
        (400, "Body field is broken somehow.", "VALIDATION_ERROR"),
        (
            400,
            (
                "Request does not match the OpenAPI specification:"
                " 'title' is a required property"
            ),
            "VALIDATION_ERROR",
        ),
        (
            401,
            (
                "Request does not match the OpenAPI specification:"
                " SecurityValidationError: Security not found."
            ),
            "UNAUTHORIZED",
        ),
        (
            500,
            (
                "Response does not match the OpenAPI specification:"
                " 7 is not of type 'string'"
            ),
            "INTERNAL_SERVER_ERROR",
        ),
        (405, "Only GET is allowed here.", "METHOD_NOT_ALLOWED"),
    ],
)
async def test_maps_error_to_stable_code(status: int, message: str, code: str):
    assert_that(
        await Envelope(status, message, "req_B2").json(),
        has_entry("error", has_entry("code", code)),
        f"'{message}' with status {status} must map to code {code}",
    )


async def test_keeps_original_message_in_body():
    assert_that(
        await Envelope(403, "The post is not published.", "req_C3").json(),
        has_entry("error", has_entry("message", "The post is not published.")),
        "The envelope must keep the original error message",
    )


async def test_stamps_request_id_in_body():
    assert_that(
        await Envelope(
            409, "Email dup@twice.example is already taken.", "req_D4"
        ).json(),
        has_entry("error", has_entry("request_id", "req_D4")),
        "The envelope must carry the request id it was given",
    )
