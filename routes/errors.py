import traceback

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi_csrf_protect.exceptions import CsrfProtectError
from sqlalchemy.exc import OperationalError
from starlette.exceptions import HTTPException as StarletteHTTPException

from core.templates import templates
from utils.logger import logger

ERROR_PAGE = "error.html"


def wants_json(request: Request) -> bool:
    return (
        "application/json" in request.headers.get("accept", "")
        or request.headers.get("x-requested-with") == "XMLHttpRequest"
    )


def http_exception_redirect(request: Request, exc: HTTPException | StarletteHTTPException):
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    if wants_json(request):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail or "Error"},
        )

    return templates.TemplateResponse(
        request=request,
        name=ERROR_PAGE,
        context={
            "status_code": exc.status_code,
            "title": "Oops! Something went wrong",
            "message": exc.detail,
            "referer": request.headers.get("referer", "/"),
        },
        status_code=exc.status_code,
    )


# Validation error handler (422)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(
        f"[VALIDATION EXCEPTION] {''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))}"
    )

    referer = request.headers.get("referer")
    return templates.TemplateResponse(
        request=request,
        name=ERROR_PAGE,
        context={
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "title": "Validation error",
            "message": "The provided data is not valid.",
            "referer": referer,
        },
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


# OperationalError handler
def operational_error_handler(request: Request, exc: OperationalError):
    logger.error(
        f"[OPERATIONAL ERROR] {''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))}"
    )

    referer = request.headers.get("referer")
    message = "The service is temporarily busy or unavailable. Please try again in a moment."

    return templates.TemplateResponse(
        request=request,
        name=ERROR_PAGE,
        context={
            "status_code": status.HTTP_503_SERVICE_UNAVAILABLE,
            "title": "Service Temporarily Unavailable",
            "message": message,
            "referer": referer,
        },
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
    )


# CSRF error handler
def csrf_protect_exception_handler(request: Request, exc: CsrfProtectError):
    logger.warning(f"CSRF error: {getattr(exc, 'message', str(exc))} | Path: {request.url.path}")

    error_message = "Invalid action. Go back and try again."

    if wants_json(request):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN, content={"detail": error_message}
        )

    referer = request.headers.get("referer")

    return templates.TemplateResponse(
        request=request,
        name=ERROR_PAGE,
        context={
            "status_code": status.HTTP_403_FORBIDDEN,
            "title": "Invalid action",
            "message": error_message,
            "referer": referer or "/",
        },
        status_code=status.HTTP_403_FORBIDDEN,
    )


# Generic exception handler
def generic_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"[GENERIC ERROR] {''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))}"
    )

    referer = request.headers.get("referer")
    message = "An unexpected error occurred. Please try again later."

    return templates.TemplateResponse(
        request=request,
        name=ERROR_PAGE,
        context={
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "title": "Internal error",
            "message": message,
            "referer": referer,
        },
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
