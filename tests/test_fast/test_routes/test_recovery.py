from hamcrest import (
    assert_that,
    contains_string,
    equal_to,
    has_entry,
    has_item,
    starts_with,
)
from tanka import Abort, Body, Empty, Get, Headers, Request, Silence

from src.routes.base import Recovery
from tests.test_fast.fakes import FakeLog


async def test_answers_with_status_of_abort():
    assert_that(
        (
            await Recovery(Silence()).response(
                Request(Get(), "/v1/posts/7f7f-0a0a", Headers(), Empty()),
                Abort(404, "Post 7f7f-0a0a does not exist."),
            )
        ).status(),
        equal_to(404),
        "The recovery must answer with the status of the abort",
    )


async def test_wraps_error_into_envelope_body():
    assert_that(
        await Body.Smart(
            (
                await Recovery(Silence()).response(
                    Request(Get(), "/v1/posts/3c3c", Headers(), Empty()),
                    Abort(403, "You are not the author of this post."),
                )
            ).body()
        ).json(),
        has_entry("error", has_entry("code", "FORBIDDEN")),
        "The recovery must wrap the error into the envelope format",
    )


async def test_stamps_request_id_on_error():
    assert_that(
        await Body.Smart(
            (
                await Recovery(Silence()).response(
                    Request(Get(), "/v1/tokens", Headers(), Empty()),
                    Abort(401, "Wrong email or password."),
                )
            ).body()
        ).json(),
        has_entry("error", has_entry("request_id", starts_with("req_"))),
        "The recovery must stamp every error with a request id",
    )


async def test_reports_answer_to_log():
    lines: list[str] = []
    await Recovery(FakeLog(lines)).response(
        Request(Get(), "/v1/tokens", Headers(), Empty()),
        Abort(401, "The refresh token is unknown."),
    )
    assert_that(
        lines,
        has_item(contains_string("/v1/tokens answered 401")),
        "The recovery must report every answered error to the log",
    )
