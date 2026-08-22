import pytest
from hamcrest import assert_that, equal_to, has_entry, has_key, is_not
from httpx import AsyncClient

from tests.test_deep.stage import account

pytestmark = [pytest.mark.online, pytest.mark.fail_slow("180s")]


async def test_registers_user_with_created_status(client: AsyncClient):
    answer = await client.post(
        "/v1/users",
        json={
            "username": "petra_paints",
            "email": "petra@art.example",
            "password": "brush&easel99",
        },
    )
    assert_that(
        answer.status_code,
        equal_to(201),
        "Registration must answer 201 Created",
    )


async def test_never_returns_password_field(client: AsyncClient):
    answer = await client.post(
        "/v1/users",
        json={
            "username": "secretive_sam",
            "email": "sam@vault.example",
            "password": "very-h1dden-pw",
        },
    )
    assert_that(
        answer.json(),
        is_not(has_key("password")),
        "The password must never appear in a response",
    )


async def test_rejects_duplicate_email_with_conflict(client: AsyncClient):
    await client.post(
        "/v1/users",
        json={
            "username": "first_franka",
            "email": "franka@twice.example",
            "password": "0riginal-pass!",
        },
    )
    answer = await client.post(
        "/v1/users",
        json={
            "username": "second_franka",
            "email": "franka@twice.example",
            "password": "an0ther-pass!",
        },
    )
    assert_that(
        answer.json(),
        has_entry("error", has_entry("code", "EMAIL_TAKEN")),
        "A duplicate email must answer with EMAIL_TAKEN",
    )


async def test_shows_own_profile_with_email(client: AsyncClient):
    owner = await account(client, "mirror_mila", "mila@self.example", "reflect10n$")
    answer = await client.get("/v1/users/me", headers=owner["header"])
    assert_that(
        answer.json(),
        has_entry("email", "mila@self.example"),
        "The own profile must include the email",
    )


async def test_hides_email_in_foreign_profile(client: AsyncClient):
    target = await account(client, "shy_sonja", "sonja@quiet.example", "wh1sper-low!")
    viewer = await account(client, "curious_carl", "carl@nosy.example", "peek1ng-carl")
    answer = await client.get(f"/v1/users/{target['id']}", headers=viewer["header"])
    assert_that(
        answer.json(),
        is_not(has_key("email")),
        "A foreign profile must not include the email",
    )


async def test_updates_own_bio_via_patch(client: AsyncClient):
    owner = await account(client, "biograf_bo", "bo@story.example", "life-l0ng-pen")
    answer = await client.patch(
        "/v1/users/me",
        json={"bio": "Now writing about tides."},
        headers=owner["header"],
    )
    assert_that(
        answer.json(),
        has_entry("bio", "Now writing about tides."),
        "The patch must update the bio of the own profile",
    )


async def test_rejects_taken_username_on_patch(client: AsyncClient):
    await account(client, "settled_stan", "stan@here.example", "st4y-put-pw!")
    mover = await account(client, "moving_max", "max@there.example", "keep-m0ving!")
    answer = await client.patch(
        "/v1/users/me",
        json={"username": "settled_stan"},
        headers=mover["header"],
    )
    assert_that(
        answer.json(),
        has_entry("error", has_entry("code", "USERNAME_TAKEN")),
        "Patching to a taken username must answer USERNAME_TAKEN",
    )


async def test_answers_not_found_for_ghost_user(client: AsyncClient):
    viewer = await account(client, "seeker_sia", "sia@search.example", "f1nd-nob0dy!")
    answer = await client.get(
        "/v1/users/e0e1e2e3-4444-4555-8666-777788889999",
        headers=viewer["header"],
    )
    assert_that(
        answer.status_code,
        equal_to(404),
        "An unknown user id must answer 404",
    )
