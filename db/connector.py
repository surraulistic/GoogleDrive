import logging
import traceback
from contextlib import contextmanager
from typing import Generator

from pydantic import PostgresDsn
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from config import settings

logger = logging.getLogger(__name__)


class DatabaseConnector:
    def __init__(self, db_url: PostgresDsn = settings.infrastructure_config.postgres_dsn):
        self.db_url = str(db_url)
        self.engine = create_engine(
            self.db_url,
            pool_recycle=28000,
            pool_pre_ping=True,
        )
        self.session_factory = sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
        )
    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        with self.session_factory() as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                logger.error(traceback.format_exc())
            finally:
                session.close()


db_connector = DatabaseConnector()


def get_db():
    with db_connector.session() as db:
        yield db