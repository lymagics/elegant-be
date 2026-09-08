from pathlib import Path

from tanka import (
    Authenticated,
    Catch,
    Delete,
    Get,
    Logging,
    Mount,
    On,
    OpenApi,
    Patch,
    Post,
    Route,
    Routes,
    Tanka,
)

from src.postgres.db import AsyncSQLAlchemyDb
from src.routes.base import Bearer, Recovery, SoftBearer
from src.routes.posts import (
    PostCreation,
    PostPage,
    PostRemoval,
    PostRenewal,
    PostView,
)
from src.routes.tokens import Grant, Revocation, TokenRenewal
from src.routes.users import OwnProfile, Profile, ProfileRenewal, Registration


class ElegantBe:
    def __init__(self, db: AsyncSQLAlchemyDb, bearer: Bearer):
        self.db = db
        self.bearer = bearer

    def app(self) -> Tanka:
        return Tanka(
            Catch(
                OpenApi(
                    str(Path(__file__).with_name("openapi.yaml")),
                    Routes(
                        Mount(
                            "/v1",
                            Routes(
                                Route(
                                    Post(),
                                    "/users",
                                    Registration(self.db),
                                ),
                                Route(
                                    Get(),
                                    "/users/me",
                                    Authenticated(OwnProfile(self.db), self.bearer),
                                ),
                                Route(
                                    Patch(),
                                    "/users/me",
                                    Authenticated(ProfileRenewal(self.db), self.bearer),
                                ),
                                Route(
                                    Get(),
                                    "/users/{id}",
                                    Authenticated(Profile(self.db), self.bearer),
                                ),
                                Route(
                                    Post(),
                                    "/tokens",
                                    Grant(self.db, self.bearer),
                                ),
                                Route(
                                    Patch(),
                                    "/tokens",
                                    TokenRenewal(self.db, self.bearer),
                                ),
                                Route(
                                    Delete(),
                                    "/tokens",
                                    Authenticated(Revocation(self.db), self.bearer),
                                ),
                                Route(
                                    Post(),
                                    "/posts",
                                    Authenticated(PostCreation(self.db), self.bearer),
                                ),
                                Route(
                                    Get(),
                                    "/posts",
                                    PostPage(self.db),
                                ),
                                Route(
                                    Get(),
                                    "/posts/{id}",
                                    Authenticated(
                                        PostView(self.db),
                                        SoftBearer(self.bearer),
                                    ),
                                ),
                                Route(
                                    Patch(),
                                    "/posts/{id}",
                                    Authenticated(PostRenewal(self.db), self.bearer),
                                ),
                                Route(
                                    Delete(),
                                    "/posts/{id}",
                                    Authenticated(PostRemoval(self.db), self.bearer),
                                ),
                            ),
                        ),
                    ),
                ),
                On(..., Recovery(Logging("app"))),
            ),
        )
