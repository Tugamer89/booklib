import time
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import settings

engine = create_engine(
    settings.database_url,
    pool_size=5,
    max_overflow=2,
    pool_timeout=30,
    pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    retries = 0
    while True:
        try:
            db = SessionLocal()
            yield db
            break
        except OperationalError as e:
            if retries >= settings.db_max_retries:
                raise e
            retries += 1
            time.sleep(settings.db_retry_delay)
        finally:
            try:
                db.close()
            except:
                pass
