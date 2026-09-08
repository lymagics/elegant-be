from http import HTTPStatus

from src.domain.json_readable import JsonReadable


class Envelope(JsonReadable):
    def __init__(self, status: int, message: str, request: str):
        self.status = status
        self.message = message
        self.request = request

    async def json(self) -> dict:
        return {
            "error": {
                "code": self._code(),
                "message": self.message,
                "request_id": self.request,
            }
        }

    def _code(self) -> str:
        fitting = {400: "VALIDATION_ERROR"}.get(
            self.status, HTTPStatus(self.status).name
        )
        for row in self._table():
            if row["saying"] in self.message:
                fitting = row["code"]
        return fitting

    def _table(self) -> list[dict]:
        return [
            {"saying": "Wrong email or password", "code": "INVALID_CREDENTIALS"},
            {"saying": "refresh token", "code": "INVALID_REFRESH_TOKEN"},
            {"saying": "User ", "code": "USER_NOT_FOUND"},
            {"saying": "Post ", "code": "POST_NOT_FOUND"},
            {"saying": "Email ", "code": "EMAIL_TAKEN"},
            {"saying": "Username ", "code": "USERNAME_TAKEN"},
        ]
