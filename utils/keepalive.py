import httpx
from sqlalchemy import text

from core.config import settings
from db.database import SessionLocal
from utils.logger import logger

async def keepalive_job():
    if not settings.keepalive_url:
        return
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.head(settings.keepalive_url, timeout=10)
            if resp.status_code == 200:
                logger.info(f"[KEEPALIVE] Successo HEAD {settings.keepalive_url}")
            else:
                logger.warning(f"[KEEPALIVE] Status {resp.status_code} su {settings.keepalive_url}")
    except Exception as e:
        logger.error(f"[KEEPALIVE] Errore: {e}")

async def keepalive_db_job():
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        logger.info("[DB-KEEPALIVE] Query di keepalive eseguita con successo.")
    except Exception as e:
        logger.error(f"[DB-KEEPALIVE] Errore: {e}")
