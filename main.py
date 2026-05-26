import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_csrf_protect import CsrfProtect
from securecookies import SecureCookiesMiddleware
from starlette.middleware.sessions import SessionMiddleware

from core.config import settings
from core.csrf import CsrfSettings
from core.middleware import PreventSessionOverwriteMiddleware
from routes import admin, auth, books, debug, errors, extras
from utils.starter import lifespan

app = FastAPI(lifespan=lifespan, title="BookLib", version="1.11.0")  # x-release-please-version


@CsrfProtect.load_config
def get_config():
    return CsrfSettings()


# Middleware per sessioni
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret_key,
    session_cookie="session",
    max_age=None,
    same_site="lax",
    https_only=not settings.DEBUG,
)

# Middleware per la compressione GZip
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Middleware per gestire il "remember me"
app.add_middleware(PreventSessionOverwriteMiddleware)

# Middleware per cookie sicuri
app.add_middleware(
    SecureCookiesMiddleware,
    secrets=[settings.csrf_secret_key],
    included_cookies=["session", "fastapi-csrf-token"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_exception_handler(errors.HTTPException, errors.http_exception_redirect)
app.add_exception_handler(errors.StarletteHTTPException, errors.http_exception_redirect)
app.add_exception_handler(errors.RequestValidationError, errors.validation_exception_handler)
app.add_exception_handler(errors.OperationalError, errors.operational_error_handler)
app.add_exception_handler(errors.CsrfProtectError, errors.csrf_protect_exception_handler)
app.add_exception_handler(Exception, errors.generic_exception_handler)

app.include_router(auth.router)
app.include_router(books.router)
app.include_router(admin.router)
app.include_router(extras.router)
if settings.DEBUG:
    app.include_router(debug.router)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "localhost")
    uvicorn.run("main:app", host=host, port=port, workers=4)
