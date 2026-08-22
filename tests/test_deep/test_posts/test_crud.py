import pytest
from hamcrest import assert_that, equal_to, has_entry
from httpx import AsyncClient

from tests.test_deep.stage import account

pytestmark = [pytest.mark.online, pytest.mark.fail_slow("180s")]


async def test_creates_post_with_author_from_token(client: AsyncClient):
    author = await account(client, "typing_tina", "tina@keys.example", "clack-cl4ck!")
    answer = await client.post(
        "/v1/posts",
        json={
            "title": "Fog over the canal",
            "content": "It rolled in before six...",
        },
        headers=author["header"],
    )
    assert_that(
        answer.json(),
        has_entry("authorId", author["id"]),
        "The created post must belong to the token owner",
    )


async def test_lists_only_published_posts_for_guests(client: AsyncClient):
    author = await account(client, "half_hana", "hana@drafts.example", "s0me-public!")
    await client.post(
        "/v1/posts",
        json={
            "title": "Visible one",
            "content": "Everyone reads this.",
            "published": True,
        },
        headers=author["header"],
    )
    await client.post(
        "/v1/posts",
        json={
            "title": "Hidden one",
            "content": "Only drafts folder.",
            "published": False,
        },
        headers=author["header"],
    )
    answer = await client.get("/v1/posts")
    assert_that(
        answer.json(),
        has_entry("meta", has_entry("total", 1)),
        "Guests must count only published posts",
    )


async def test_shows_unpublished_post_to_its_author(client: AsyncClient):
    author = await account(client, "draft_dora", "dora@wip.example", "n0t-done-yet!")
    draft = (
        await client.post(
            "/v1/posts",
            json={
                "title": "Unfinished symphony",
                "content": "Movement two pending.",
                "published": False,
            },
            headers=author["header"],
        )
    ).json()
    answer = await client.get(f"/v1/posts/{draft['id']}", headers=author["header"])
    assert_that(
        answer.status_code,
        equal_to(200),
        "The author must see the own unpublished post",
    )


async def test_hides_unpublished_post_from_stranger(client: AsyncClient):
    author = await account(client, "private_pia", "pia@mine.example", "keep-0ut-all")
    stranger = await account(
        client, "peeking_pete", "pete@spy.example", "let-me-1n-pls"
    )
    draft = (
        await client.post(
            "/v1/posts",
            json={
                "title": "Diary page",
                "content": "Do not read.",
                "published": False,
            },
            headers=author["header"],
        )
    ).json()
    answer = await client.get(f"/v1/posts/{draft['id']}", headers=stranger["header"])
    assert_that(
        answer.json(),
        has_entry("error", has_entry("code", "FORBIDDEN")),
        "A stranger must not see an unpublished post",
    )


async def test_updates_own_post_title(client: AsyncClient):
    author = await account(client, "editor_edda", "edda@fix.example", "rewr1te-it!")
    draft = (
        await client.post(
            "/v1/posts",
            json={
                "title": "Rough sketch",
                "content": "First take.",
            },
            headers=author["header"],
        )
    ).json()
    answer = await client.patch(
        f"/v1/posts/{draft['id']}",
        json={"title": "Polished piece", "published": True},
        headers=author["header"],
    )
    assert_that(
        answer.json(),
        has_entry("title", "Polished piece"),
        "The patch must update the title of the own post",
    )


async def test_forbids_foreign_post_update(client: AsyncClient):
    author = await account(client, "owner_olek", "olek@land.example", "th1s-is-mine")
    intruder = await account(client, "brazen_bela", "bela@grab.example", "g1ve-it-here")
    post = (
        await client.post(
            "/v1/posts",
            json={
                "title": "My garden notes",
                "content": "Tomatoes doing fine.",
                "published": True,
            },
            headers=author["header"],
        )
    ).json()
    answer = await client.patch(
        f"/v1/posts/{post['id']}",
        json={"title": "Stolen notes"},
        headers=intruder["header"],
    )
    assert_that(
        answer.status_code,
        equal_to(403),
        "A foreign post must not be updatable",
    )


async def test_removes_own_post_for_good(client: AsyncClient):
    author = await account(client, "cleaner_cleo", "cleo@tidy.example", "sw33p-away!")
    post = (
        await client.post(
            "/v1/posts",
            json={
                "title": "Regretted rant",
                "content": "Too spicy for the web.",
                "published": True,
            },
            headers=author["header"],
        )
    ).json()
    await client.delete(f"/v1/posts/{post['id']}", headers=author["header"])
    answer = await client.get(f"/v1/posts/{post['id']}")
    assert_that(
        answer.status_code,
        equal_to(404),
        "A removed post must be gone for good",
    )


async def test_answers_not_found_for_ghost_post(client: AsyncClient):
    answer = await client.get("/v1/posts/a1a2a3a4-b5b6-4c7c-8d8d-e9e9f0f0a1a1")
    assert_that(
        answer.json(),
        has_entry("error", has_entry("code", "POST_NOT_FOUND")),
        "An unknown post id must answer POST_NOT_FOUND",
    )


async def test_filters_posts_by_author_query(client: AsyncClient):
    prolific = await account(client, "busy_bora", "bora@many.example", "wr1te-a-lot!")
    other = await account(client, "single_sven", "sven@once.example", "just-0ne-post")
    await client.post(
        "/v1/posts",
        json={
            "title": "Bora one",
            "content": "First of two.",
            "published": True,
        },
        headers=prolific["header"],
    )
    await client.post(
        "/v1/posts",
        json={
            "title": "Bora two",
            "content": "Second of two.",
            "published": True,
        },
        headers=prolific["header"],
    )
    await client.post(
        "/v1/posts",
        json={
            "title": "Sven only",
            "content": "The single one.",
            "published": True,
        },
        headers=other["header"],
    )
    answer = await client.get(f"/v1/posts?authorId={prolific['id']}")
    assert_that(
        answer.json(),
        has_entry("meta", has_entry("total", 2)),
        "The author filter must count only that author's posts",
    )
