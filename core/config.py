from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL")
    session_secret_key: str = os.getenv("SESSION_SECRET")
    csrf_secret_key: str = os.getenv("CSRF_SECRET")
    csrf_token_location: str = "body"
    csrf_token_key: str = "csrf_token"
    allowed_extensions: set = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
    allowed_mime_types: set = {
        "image/jpeg", "image/png", "image/gif", "image/bmp", "image/webp"
    }
    username_regex: str = r"^[a-zA-Z0-9_.-]{3,20}$"
    password_regex: str = r"^.{8,100}$"

settings = Settings()
