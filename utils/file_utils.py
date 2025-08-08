import os
import shutil
import uuid
import magic
import requests
from fastapi import HTTPException
from core.config import settings

def validate_and_save_cover(cover):
    ext = os.path.splitext(cover.filename)[-1].lower()
    if ext not in settings.allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Estensione file non valida: {ext}")

    sample = cover.file.read(2048)
    mime_type = magic.from_buffer(sample, mime=True)
    if mime_type not in settings.allowed_mime_types:
        raise HTTPException(status_code=400, detail=f"Tipo MIME non valido: {mime_type}")

    cover.file.seek(0)
    os.makedirs("static/covers", exist_ok=True)
    cover_path = f"static/covers/{uuid.uuid4().hex}{ext}"
    with open(cover_path, "wb") as buffer:
        shutil.copyfileobj(cover.file, buffer)
    return cover_path

def validate_cover_url(cover_url: str) -> str:
    cover_path = cover_url.strip()
    
    if not cover_path.startswith("http://") and not cover_path.startswith("https://"):
        raise HTTPException(status_code=400, detail="URL della copertina non valido")
    
    try:
        response = requests.head(cover_path, timeout=5)
        content_type = response.headers.get("Content-Type", "")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Errore durante la verifica dell'URL dell'immagine: {e}.")
    
    if content_type not in settings.allowed_mime_types:
        raise HTTPException(status_code=400, detail=f"URL non valido: tipo MIME non valido ({content_type}).")
    
    return cover_path
