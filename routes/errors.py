from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import OperationalError
from fastapi.templating import Jinja2Templates

from utils.logger import logger

templates = Jinja2Templates(directory="templates")

def wants_json(request: Request) -> bool:
    return "application/json" in request.headers.get("accept", "") or \
           request.headers.get("x-requested-with") == "XMLHttpRequest"

async def http_exception_redirect(request: Request, exc: HTTPException | StarletteHTTPException):
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    if wants_json(request):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail or "Errore"},
        )

    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "status_code": exc.status_code,
            "title": "Oops! Qualcosa è andato storto",
            "message": exc.detail,
            "referer": request.headers.get("referer", "/")
        },
        status_code=exc.status_code
    )

# Gestione errori di validazione (422)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    referer = request.headers.get("referer")
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "title": "Errore di validazione",
            "message": "I dati forniti non sono validi.",
            "referer": referer
        },
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )

# Gestione OperationalError
async def operational_error_handler(request: Request, exc: OperationalError):
    import traceback
    logger.error(f"[OPERATIONAL ERROR] {''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))}")

    referer = request.headers.get("referer")
    message = (
        "Il servizio è temporaneamente occupato o non disponibile. "
        "Riprova tra qualche istante."
    )
    
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "status_code": status.HTTP_503_SERVICE_UNAVAILABLE,
            "title": "Servizio Temporaneamente Non Disponibile",
            "message": message,
            "referer": referer
        },
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE
    )

# Gestione eccezioni generiche
async def generic_exception_handler(request: Request, exc: Exception):
    import traceback
    logger.error(f"[GENERIC ERROR] {''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))}")

    referer = request.headers.get("referer")
    message = (
        "Si è verificato un errore imprevisto. "
        "Riprova più tardi."
    )

    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "title": "Errore interno",
            "message": message,
            "referer": referer,
        },
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
