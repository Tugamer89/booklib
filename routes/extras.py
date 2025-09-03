from fastapi import APIRouter
from fastapi.responses import FileResponse, Response

router = APIRouter()

# Keepalive route
@router.head("/keepalive")
async def keepalive():
    return Response(status_code=200)

# Favicon route
@router.get("/favicon.ico")
async def favicon():
    return FileResponse("static/favicon.ico")
