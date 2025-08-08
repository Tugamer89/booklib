from fastapi_csrf_protect import CsrfProtect
from pydantic_settings import BaseSettings
from core.config import settings

class CsrfSettings(BaseSettings):
    secret_key: str = settings.csrf_secret_key
    token_location: str = settings.csrf_token_location
    token_key: str = settings.csrf_token_key

@CsrfProtect.load_config
def get_csrf_config():
    return CsrfSettings()
