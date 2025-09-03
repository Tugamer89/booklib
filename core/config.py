from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pydantic_settings.sources import PydanticBaseSettingsSource
from pydantic import Field
import cloudinary
import os

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
    allowed_mime_types: set = {
        "image/jpeg", "image/png", "image/gif", "image/bmp", "image/webp"
    }
    username_regex: str = r"^[a-zA-Z0-9_.-]{3,20}$"
    password_regex: str = r"^.{8,100}$"
    db_max_retries: int = 3
    db_retry_delay: int = 1 # seconds
    max_sessions_per_user: int = 5
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    admin_users_env: str = Field(default=os.getenv("ADMIN_USERS", ""), repr=False)
    admin_users: set[str] = set()
    keepalive_url: str = os.getenv("KEEPALIVE_URL", "")
    keepalive_cron: str = os.getenv("KEEPALIVE_CRON", "*/10 * * * *")
    keepalive_db_cron: str = os.getenv("KEEPALIVE_DB_CRON", "0 0 */5 * *")

    def __init__(self, **data):
        super().__init__(**data)
        self.admin_users = {
            u.strip()
            for u in self.admin_users_env.split(",")
            if u.strip()
        }

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
    api_secret=settings.cloudinary_api_secret
)
