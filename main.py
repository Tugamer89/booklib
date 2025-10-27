import os
import uvicorn

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from securecookies import SecureCookiesMiddleware
from starlette.middleware.sessions import SessionMiddleware

from core.config import settings
from routes import admin, auth, books, debug, errors, extras
from utils.starter import lifespan


app = FastAPI(lifespan=lifespan, title="BookLib", version="1.5.1")

# Middleware per sessioni
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret_key,
    session_cookie="session",
    max_age=7 * 24 * 3600,  # 7 giorni
    same_site="lax"
)

# Middleware per cookie sicuri e protezione CSRF
app.add_middleware(
    SecureCookiesMiddleware,
    secrets=[settings.csrf_secret_key],
    included_cookies=["session", "fastapi-csrf-token"]
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_exception_handler(errors.HTTPException, errors.http_exception_redirect)
app.add_exception_handler(errors.StarletteHTTPException, errors.http_exception_redirect)
app.add_exception_handler(errors.RequestValidationError, errors.validation_exception_handler)
app.add_exception_handler(errors.OperationalError, errors.operational_error_handler)
app.add_exception_handler(Exception, errors.generic_exception_handler)

app.include_router(auth.router)
app.include_router(books.router)
app.include_router(admin.router)
app.include_router(extras.router)
if settings.DEBUG:
    app.include_router(debug.router)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, workers=4)
