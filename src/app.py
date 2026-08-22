from fastapi import APIRouter, FastAPI
from fastapi.exceptions import RequestValidationError

from src.routes.base import Recovery, invalid


class Application:
    def __init__(self, *routers: APIRouter):
        self.routers = routers

    def app(self) -> FastAPI:
        app = FastAPI(title="Blogging API", version="1")
        app.add_middleware(Recovery)
        app.add_exception_handler(RequestValidationError, invalid)
        for router in self.routers:
            app.include_router(router, prefix="/v1")
        return app
