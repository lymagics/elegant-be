from src.domain.json_readable import JsonReadable


class Envelope(JsonReadable):
    def __init__(self, error: Exception, request: str):
        self.error = error
        self.request = request

    def status(self) -> int:
        return self._row()["status"]

    async def json(self) -> dict:
        return {
            "error": {
                "code": self._row()["code"],
                "message": str(self.error),
                "request_id": self.request,
            }
        }

    def _row(self) -> dict:
        fitting = {"status": 400, "code": "VALIDATION_ERROR"}
        for row in self._table():
            if row["saying"] in str(self.error):
                fitting = row
        return fitting

    def _table(self) -> list[dict]:
        return [
            {
                "saying": "Wrong email or password",
                "status": 401,
                "code": "INVALID_CREDENTIALS",
            },
            {
                "saying": "access token is missing",
                "status": 401,
                "code": "UNAUTHORIZED",
            },
            {
                "saying": "access token is not valid",
                "status": 401,
                "code": "UNAUTHORIZED",
            },
            {
                "saying": "refresh token",
                "status": 401,
                "code": "INVALID_REFRESH_TOKEN",
            },
            {
                "saying": "User ",
                "status": 404,
                "code": "USER_NOT_FOUND",
            },
            {
                "saying": "Post ",
                "status": 404,
                "code": "POST_NOT_FOUND",
            },
            {
                "saying": "Email ",
                "status": 409,
                "code": "EMAIL_TAKEN",
            },
            {
                "saying": "Username ",
                "status": 409,
                "code": "USERNAME_TAKEN",
            },
            {
                "saying": "not the author",
                "status": 403,
                "code": "FORBIDDEN",
            },
            {
                "saying": "not published",
                "status": 403,
                "code": "FORBIDDEN",
            },
        ]
