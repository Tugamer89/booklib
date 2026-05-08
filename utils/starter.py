from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI
from sqlalchemy import text

from core.config import settings
from db.database import Base, engine
from utils.keepalive import keepalive_db_job, keepalive_job
from utils.logger import logger

scheduler = AsyncIOScheduler()


def try_acquire_lock(lock_id: int = 12345) -> bool:
    with engine.begin() as conn:
        result = conn.execute(text("SELECT pg_try_advisory_lock(:id)"), {"id": lock_id})
        acquired = result.scalar()
    return acquired


def release_lock(lock_id: int = 12345):
    with engine.begin() as conn:
        conn.execute(text("SELECT pg_advisory_unlock(:id)"), {"id": lock_id})


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)

    lock_acquired = try_acquire_lock()
    if lock_acquired:
        logger.info("[KEEPALIVE] Lock acquired, starting scheduler...")

        # HTTP keepalive
        if settings.keepalive_url:
            scheduler.add_job(
                keepalive_job,
                trigger=CronTrigger.from_crontab(settings.keepalive_cron),
                id="keepalive_http",
                replace_existing=True,
            )
            logger.info(f"[KEEPALIVE] HTTP job started with cron: {settings.keepalive_cron}")

        # DB keepalive
        scheduler.add_job(
            keepalive_db_job,
            trigger=CronTrigger.from_crontab(settings.keepalive_db_cron),
            id="keepalive_db",
            replace_existing=True,
        )
        logger.info(f"[KEEPALIVE] DB job started with cron: {settings.keepalive_db_cron}")

        if not scheduler.running:
            scheduler.start()

    try:
        yield
    finally:
        if lock_acquired and scheduler.running:
            scheduler.shutdown(wait=False)
            release_lock()
            logger.info("[KEEPALIVE] Scheduler shutdown and lock released.")
