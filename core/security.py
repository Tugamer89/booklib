import re
from fastapi import HTTPException, status
from core.config import settings

def validate_credentials(username: str, password: str):
    if not re.match(settings.username_regex, username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username non valido.")
    if not re.match(settings.password_regex, password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password troppo corta o non valida.")
