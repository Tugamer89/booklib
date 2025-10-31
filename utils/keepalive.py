import httpx
from sqlalchemy import text

from core.config import settings
from db.database import engine
from utils.logger import logger

async def keepalive_job():
    if not settings.keepalive_url:
        return
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.head(settings.keepalive_url, timeout=10)
            if resp.status_code == 200:
                logger.info(f"[KEEPALIVE] Success HEAD {settings.keepalive_url}")
            else:
                logger.warning(f"[KEEPALIVE] Status {resp.status_code} on {settings.keepalive_url}")
    except Exception as e:
        logger.error(f"[HTTP-KEEPALIVE]: {e}")

def keepalive_db_job():
    if not settings.keepalive_db:
        return
    try:
        with engine.begin() as db:
            db.execute(text("SELECT 1"))
        logger.info("[KEEPALIVE] Success keepalive query.")
    except Exception as e:
        logger.error(f"[DB-KEEPALIVE]: {e}")
