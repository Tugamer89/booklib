from pydantic_settings import BaseSettings
from dotenv import load_dotenv
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
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    cloudinary.config(
        cloud_name=cloudinary_cloud_name,
        api_key=cloudinary_api_key,
        api_secret=cloudinary_api_secret
    )

settings = Settings()
