from fastapi import Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import OperationalError

from core.templates import templates

# Gestione HTTPException
async def http_exception_redirect(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 401:
        return RedirectResponse(url="/auth", status_code=302)
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "status_code": exc.status_code,
            "title": "Oops! Qualcosa è andato storto",
            "message": exc.detail if exc.detail else "Errore imprevisto"
        },
        status_code=exc.status_code
    )

# Gestione errori di validazione (422)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "status_code": 422,
            "title": "Errore di validazione",
            "message": "I dati forniti non sono validi."
        },
        status_code=422
    )

# Gestione OperationalError
async def operational_error_handler(request: Request, exc: OperationalError):
    import traceback
    print("OperationalError:", "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)))

    message = (
        "Il servizio è temporaneamente occupato o non disponibile. "
        "Riprova tra qualche istante."
    )
    
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "status_code": 503,
            "title": "Servizio Temporaneamente Non Disponibile",
            "message": message
        },
        status_code=503
    )

# Gestione eccezioni generiche
async def generic_exception_handler(request: Request, exc: Exception):
    # Log dell'errore vero per debugging
    import traceback
    print("ERRORE GENERICO:", "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)))

    message = (
        "Si è verificato un errore imprevisto. "
        "Riprova più tardi."
    )

    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "status_code": 500,
            "title": "Errore interno",
            "message": message
        },
        status_code=500
    )
