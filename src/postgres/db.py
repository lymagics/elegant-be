from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine


class AsyncSQLAlchemyDb:
    def __init__(self, url: str):
        self.engine = create_async_engine(url)

    async def db(self) -> AsyncIterator[AsyncSession]:
        async with (
            AsyncSession(self.engine, expire_on_commit=False) as session,
            session.begin(),
        ):
            yield session
