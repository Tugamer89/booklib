import ipaddress
import os
import socket
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
            status_code=status.HTTP_400_BAD_REQUEST, detail="File too large, maximum 10 MB"
        )

    cover.file.seek(0)

    ext = os.path.splitext(cover.filename)[-1].lower()
    if ext not in settings.allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid file extension: {ext}"
        )

    sample = cover.file.read(2048)
    mime_type = magic.from_buffer(sample, mime=True)
    if mime_type not in settings.allowed_mime_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid MIME type: {mime_type}"
        )

    cover.file.seek(0)

    result = cloudinary.uploader.upload(cover.file, folder="booklib/covers")
    return result["secure_url"]


def validate_cover_url(cover_url: str) -> str:
    cover_path = cover_url.strip()

    if not cover_path.startswith(("http://", "https://")):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid cover URL")

    try:
        parsed = urlparse(cover_path)
        hostname = parsed.hostname
        if not hostname:
            raise ValueError("No hostname found")

        ip_addr = socket.gethostbyname(hostname)
        ip = ipaddress.ip_address(ip_addr)
        # Security: Prevent SSRF by ensuring only public, global non-multicast IPs are allowed
        if not ip.is_global or ip.is_multicast:
            raise ValueError("Private, loopback, or invalid IP addresses are not allowed")

        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        safe_url = f"{parsed.scheme}://{ip_addr}:{port}{parsed.path}"
        if parsed.query:
            safe_url += f"?{parsed.query}"

        response = requests.head(
            safe_url, headers={"Host": hostname}, timeout=5, allow_redirects=False
        )
        if response.is_redirect:
            raise ValueError("Redirects are not allowed for security reasons")
        content_type = response.headers.get("Content-Type", "")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error verifying image URL: {e}.",
        ) from None

    if content_type not in settings.allowed_mime_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid URL: unsupported MIME type ({content_type}).",
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
