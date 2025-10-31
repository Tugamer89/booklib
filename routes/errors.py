import traceback
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import OperationalError
from fastapi_csrf_protect.exceptions import CsrfProtectError

from core.templates import templates
from utils.logger import logger

ERROR_PAGE = "error.html"


def wants_json(request: Request) -> bool:
    return "application/json" in request.headers.get("accept", "") or \
           request.headers.get("x-requested-with") == "XMLHttpRequest"

def http_exception_redirect(request: Request, exc: HTTPException | StarletteHTTPException):
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    if wants_json(request):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail or "Errore"},
        )

    return templates.TemplateResponse(
        ERROR_PAGE,
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
def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"[VALIDATION EXCEPTION] {''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))}")
    
    referer = request.headers.get("referer")
    return templates.TemplateResponse(
        ERROR_PAGE,
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
def operational_error_handler(request: Request, exc: OperationalError):
    logger.error(f"[OPERATIONAL ERROR] {''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))}")

    referer = request.headers.get("referer")
    message = (
        "Il servizio è temporaneamente occupato o non disponibile. "
        "Riprova tra qualche istante."
    )
    
    return templates.TemplateResponse(
        ERROR_PAGE,
        {
            "request": request,
            "status_code": status.HTTP_503_SERVICE_UNAVAILABLE,
            "title": "Servizio Temporaneamente Non Disponibile",
            "message": message,
            "referer": referer
        },
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE
    )

# Gestione eccezioni per CSRF errato
def csrf_protect_exception_handler(request: Request, exc: CsrfProtectError):
    logger.warning(f"CSRF error: {getattr(exc, 'message', str(exc))} | Path: {request.url.path}")

    error_message = "Azione non valida. Torna indietro e riprova."

    if wants_json(request):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": error_message}
        )

    referer = request.headers.get("referer")

    return templates.TemplateResponse(
        ERROR_PAGE,
        {
            "request": request,
            "status_code": status.HTTP_403_FORBIDDEN,
            "title": "Azione non valida",
            "message": error_message,
            "referer": referer or "/",
        },
        status_code=status.HTTP_403_FORBIDDEN,
    )

# Gestione eccezioni generiche
def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"[GENERIC ERROR] {''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))}")

    referer = request.headers.get("referer")
    message = (
        "Si è verificato un errore imprevisto. "
        "Riprova più tardi."
    )

    return templates.TemplateResponse(
        ERROR_PAGE,
        {
            "request": request,
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "title": "Errore interno",
            "message": message,
            "referer": referer,
        },
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
