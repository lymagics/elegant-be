from httpx import AsyncClient


async def account(
    client: AsyncClient, username: str, email: str, password: str
) -> dict:
    profile = (
        await client.post(
            "/v1/users",
            json={
                "username": username,
                "email": email,
                "password": password,
            },
        )
    ).json()
    grant = (
        await client.post("/v1/tokens", json={"email": email, "password": password})
    ).json()
    return {
        "id": profile["id"],
        "header": {"Authorization": f"Bearer {grant['accessToken']}"},
    }
