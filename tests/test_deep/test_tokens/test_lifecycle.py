import pytest
from hamcrest import assert_that, equal_to, has_entry, has_key
from httpx import AsyncClient

pytestmark = [pytest.mark.online, pytest.mark.fail_slow("180s")]


async def test_issues_token_pair_for_valid_credentials(client: AsyncClient):
    await client.post(
        "/v1/users",
        json={
            "username": "login_lena",
            "email": "lena@enter.example",
            "password": "0pen-sesame-9",
        },
    )
    answer = await client.post(
        "/v1/tokens",
        json={
            "email": "lena@enter.example",
            "password": "0pen-sesame-9",
        },
    )
    assert_that(
        answer.json(),
        has_key("accessToken"),
        "A valid login must answer with an access token",
    )


async def test_rejects_wrong_password_on_login(client: AsyncClient):
    await client.post(
        "/v1/users",
        json={
            "username": "guarded_greg",
            "email": "greg@fort.example",
            "password": "the-0nly-key!",
        },
    )
    answer = await client.post(
        "/v1/tokens",
        json={
            "email": "greg@fort.example",
            "password": "a-wr0ng-key!!",
        },
    )
    assert_that(
        answer.json(),
        has_entry("error", has_entry("code", "INVALID_CREDENTIALS")),
        "A wrong password must answer INVALID_CREDENTIALS",
    )


async def test_refreshes_access_token_via_cookie(client: AsyncClient):
    await client.post(
        "/v1/users",
        json={
            "username": "rotating_rita",
            "email": "rita@spin.example",
            "password": "turn-ar0und-4",
        },
    )
    await client.post(
        "/v1/tokens",
        json={
            "email": "rita@spin.example",
            "password": "turn-ar0und-4",
        },
    )
    answer = await client.patch("/v1/tokens")
    assert_that(
        answer.status_code,
        equal_to(200),
        "The refresh with a living cookie must answer 200",
    )


async def test_rejects_refresh_without_cookie(client: AsyncClient):
    answer = await client.patch("/v1/tokens")
    assert_that(
        answer.json(),
        has_entry("error", has_entry("code", "INVALID_REFRESH_TOKEN")),
        "Refreshing without a cookie must answer INVALID_REFRESH_TOKEN",
    )


async def test_ends_session_with_no_content(client: AsyncClient):
    await client.post(
        "/v1/users",
        json={
            "username": "leaving_leo",
            "email": "leo@exit.example",
            "password": "g00dbye-all!",
        },
    )
    grant = (
        await client.post(
            "/v1/tokens",
            json={
                "email": "leo@exit.example",
                "password": "g00dbye-all!",
            },
        )
    ).json()
    answer = await client.delete(
        "/v1/tokens",
        headers={"Authorization": f"Bearer {grant['accessToken']}"},
    )
    assert_that(
        answer.status_code,
        equal_to(204),
        "The logout must answer 204 No Content",
    )


async def test_blocks_refresh_after_logout(client: AsyncClient):
    await client.post(
        "/v1/users",
        json={
            "username": "gone_gala",
            "email": "gala@away.example",
            "password": "n0-coming-back",
        },
    )
    grant = (
        await client.post(
            "/v1/tokens",
            json={
                "email": "gala@away.example",
                "password": "n0-coming-back",
            },
        )
    ).json()
    cookie = client.cookies.get("refreshToken")
    await client.delete(
        "/v1/tokens",
        headers={"Authorization": f"Bearer {grant['accessToken']}"},
    )
    client.cookies.set("refreshToken", cookie, domain="stage", path="/v1/tokens")
    answer = await client.patch("/v1/tokens")
    assert_that(
        answer.status_code,
        equal_to(401),
        "A revoked refresh token must not refresh anymore",
    )
