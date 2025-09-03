from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from contextlib import asynccontextmanager
from fastapi import FastAPI

from core.config import settings
from db.database import engine, Base
from utils.keepalive import keepalive_job, keepalive_db_job
from utils.logger import logger

scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    
    # Keepalive HTTP
    if settings.keepalive_url:
        scheduler.add_job(
            keepalive_job,
            trigger=CronTrigger.from_crontab(settings.keepalive_cron),
            id="keepalive_http",
            replace_existing=True,
        )
        logger.info(f"[KEEPALIVE] HTTP job started with cron: {settings.keepalive_cron}")
        
    # Keepalive DB
    scheduler.add_job(
        keepalive_db_job,
        trigger=CronTrigger.from_crontab(settings.keepalive_db_cron),
        id="keepalive_db",
        replace_existing=True,
    )
    logger.info(f"[KEEPALIVE] DB job started with cron: {settings.keepalive_db_cron}")
    
    if not scheduler.running:
        scheduler.start()
    
    yield
    
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info(f"[KEEPALIVE] Scheduler shutdown.")
