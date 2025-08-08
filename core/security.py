import re
from fastapi import HTTPException
from core.config import settings

def validate_credentials(username: str, password: str):
    if not re.match(settings.username_regex, username):
        raise HTTPException(status_code=400, detail="Username non valido.")
    if not re.match(settings.password_regex, password):
        raise HTTPException(status_code=400, detail="Password troppo corta o non valida.")
