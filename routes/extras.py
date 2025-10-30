from fastapi import APIRouter
from fastapi.responses import FileResponse, Response, JSONResponse

router = APIRouter()

# Keepalive route
@router.head("/keepalive")
async def keepalive():
    return Response(status_code=200)

# Favicon route
@router.get("/favicon.ico")
async def favicon():
    return FileResponse("static/favicon.ico")

# Rotta per Chrome DevTools
@router.get("/.well-known/appspecific/com.chrome.devtools.json")
async def chrome_devtools():
    return JSONResponse(content=[])
