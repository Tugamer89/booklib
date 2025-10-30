from fastapi import APIRouter
from fastapi.responses import FileResponse, Response, JSONResponse

router = APIRouter()

@router.head("/keepalive")
async def keepalive():
    return Response(status_code=200)

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
