from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from db.database import get_db

router = APIRouter()

@router.head("/keepalive")
async def keepalive(db: Session = Depends(get_db)):
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
