import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from pydantic import PostgresDsn
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from config import settings


class AsyncDatabaseConnector:
    def __init__(self, db_url: PostgresDsn = settings.infrastructure_config.postgres_dsn):
        self.db_url = str(db_url)

        self.engine = create_async_engine(
            self.db_url,
            pool_recycle=28000,
            pool_pre_ping=True,
        )

        self.session_factory = async_sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
        )

    def async_session(self) -> AsyncGenerator[AsyncSession, None]:
        @asynccontextmanager
        async def _session_gen():
            async with self.session_factory() as session:
                try:
                    yield session
                    await session.commit()
                except Exception:
                    await session.rollback()
                finally:
                    await session.close()
        return _session_gen()


db_connector = AsyncDatabaseConnector()