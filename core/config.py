import os

import cloudinary
from dotenv import load_dotenv
from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher
from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings.sources import PydanticBaseSettingsSource

load_dotenv()


class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL")
    session_secret_key: str = os.getenv("SESSION_SECRET")
    csrf_secret_key: str = os.getenv("CSRF_SECRET")
    csrf_token_location: str = "body"
    csrf_token_key: str = "csrf_token"
    cloudinary_cloud_name: str = os.getenv("CLOUDINARY_CLOUD_NAME")
    cloudinary_api_key: str = os.getenv("CLOUDINARY_API_KEY")
    cloudinary_api_secret: str = os.getenv("CLOUDINARY_API_SECRET")
    allowed_extensions: set = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
    allowed_mime_types: set = {"image/jpeg", "image/png", "image/gif", "image/bmp", "image/webp"}
    username_regex: str = r"^[a-zA-Z0-9_.-]{3,20}$"
    password_regex: str = r"^.{8,100}$"
    email_regex: str = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

    db_max_retries: int = 3
    db_retry_delay_seconds: int = 1
    max_sessions_per_user: int = 5
    password_reset_token_expire_minutes: int = 15

    session_cookie_max_age_days: int = 30
    session_cookie_max_age_seconds: int = Field(0, repr=False)

    BREVO_API_KEY: str = os.getenv("BREVO_API_KEY", "")
    BREVO_EMAIL_FROM_ADDRESS: str = os.getenv("BREVO_EMAIL_FROM_ADDRESS", "noreply@example.com")
    BREVO_EMAIL_FROM_NAME: str = os.getenv("BREVO_EMAIL_FROM_NAME", "BookLib")

    app_base_url: str = os.getenv("APP_BASE_URL", "")

    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    admin_users_env: str = Field(default=os.getenv("ADMIN_USERS", ""), repr=False)
    admin_users: set[str] = set()
    keepalive_url: str = os.getenv("KEEPALIVE_URL", "")
    keepalive_cron: str = os.getenv("KEEPALIVE_CRON", "*/10 * * * *")
    keepalive_db: str = os.getenv("KEEPALIVE_DB", "")
    keepalive_db_cron: str = os.getenv("KEEPALIVE_DB_CRON", "0 0 */5 * *")

    google_books_api_key: str = os.getenv("GOOGLE_BOOKS_API_KEY", "")

    password_hash: PasswordHash = PasswordHash((BcryptHasher(),))

    def __init__(self, **data):
        super().__init__(**data)
        self.admin_users = {u.strip() for u in self.admin_users_env.split(",") if u.strip()}
        self.session_cookie_max_age_seconds = self.session_cookie_max_age_days * 24 * 60 * 60

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return init_settings, file_secret_settings


settings = Settings()
cloudinary.config(
    cloud_name=settings.cloudinary_cloud_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret,
)
