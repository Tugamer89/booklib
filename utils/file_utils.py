import os
from urllib.parse import urlparse

import cloudinary.uploader
import magic
import requests
from fastapi import HTTPException, status

from core.config import settings


def validate_and_save_cover(cover):
    cover.file.seek(0, 2)
    size = cover.file.tell()
    if size > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="File troppo grande, massimo 10 MB"
        )

    cover.file.seek(0)

    ext = os.path.splitext(cover.filename)[-1].lower()
    if ext not in settings.allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Estensione file non valida: {ext}"
        )

    sample = cover.file.read(2048)
    mime_type = magic.from_buffer(sample, mime=True)
    if mime_type not in settings.allowed_mime_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Tipo MIME non valido: {mime_type}"
        )

    cover.file.seek(0)

    result = cloudinary.uploader.upload(cover.file, folder="booklib/covers")
    return result["secure_url"]


def validate_cover_url(cover_url: str) -> str:
    cover_path = cover_url.strip()

    if not cover_path.startswith(("http://", "https://")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="URL della copertina non valido"
        )

    try:
        response = requests.head(cover_path, timeout=5)
        content_type = response.headers.get("Content-Type", "")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Errore durante la verifica dell'URL dell'immagine: {e}.",
        ) from None

    if content_type not in settings.allowed_mime_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"URL non valido: tipo MIME non valido ({content_type}).",
        )

    return cover_path


def extract_public_id(url: str) -> str:
    path = urlparse(url).path
    parts = path.split("/")
    public_id_with_ext = "/".join(parts[5:])
    public_id = public_id_with_ext.rsplit(".", 1)[0]
    return public_id


def delete_cover_from_cloudinary(url: str):
    public_id = extract_public_id(url)
    result = cloudinary.uploader.destroy(public_id)
    return result
