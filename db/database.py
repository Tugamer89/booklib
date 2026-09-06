import asyncio

from fastapi.concurrency import run_in_threadpool
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base, sessionmaker

from core.config import settings

engine = create_engine(
    settings.database_url, pool_size=5, max_overflow=2, pool_timeout=30, pool_pre_ping=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


async def get_db():
    retries = 0
    while True:
        try:
            db = await run_in_threadpool(SessionLocal)
            yield db
            break
        except OperationalError as e:
            if retries >= settings.db_max_retries:
                raise e
            retries += 1
            await asyncio.sleep(settings.db_retry_delay_seconds)
        finally:
            if 'db' in locals():
                await run_in_threadpool(db.close)
