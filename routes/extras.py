from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from core.auth import get_authenticated_user
from core.config import settings
from db.database import get_db
from db.models import User

router = APIRouter()


@router.get("/api/search-google-books")
async def proxy_google_books(
    q: str,
    max_results: int = 20,
    start_index: int = 0,
    current_user=Annotated[User, Depends(get_authenticated_user)],
):
    """
    Secure backend proxy for Google Books API to hide the API key from clients.
    """
    if not settings.google_books_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google API Key is not configured on the server.",
        )

    url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        "q": q,
        "maxResults": max_results,
        "startIndex": start_index,
        "key": settings.google_books_api_key,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail="Failed to fetch data from Google Books API.",
            ) from e
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error communicating with external API.",
            ) from e


@router.head("/keepalive")
async def keepalive(db: Annotated[Session, Depends(get_db)]):
    try:
        db.execute(text("SELECT 1"))
        return Response(status_code=status.HTTP_200_OK)
    except Exception:
        return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)


@router.get("/favicon.ico")
async def favicon():
    return FileResponse("static/favicon.ico")


@router.get("/manifest.json")
async def get_manifest():
    return FileResponse("manifest.json")


@router.get("/sw.js")
async def get_service_worker():
    return FileResponse("static/js/sw.js", media_type="application/javascript")


@router.get("/.well-known/appspecific/com.chrome.devtools.json")
async def chrome_devtools():
    return JSONResponse(content=[])
