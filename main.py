from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from securecookies import SecureCookiesMiddleware

from db.database import engine, Base
from core.config import settings
from routes import auth, books, debug, errors


app = FastAPI()


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
app.add_exception_handler(errors.RequestValidationError, errors.validation_exception_handler)
app.add_exception_handler(errors.OperationalError, errors.operational_error_handler)
app.add_exception_handler(Exception, errors.generic_exception_handler)

app.include_router(auth.router)
app.include_router(books.router)
if settings.DEBUG:
    app.include_router(debug.router)


@app.on_event("startup")
async def on_startup():
    Base.metadata.create_all(bind=engine)

# Favicon route
@app.get("/favicon.ico")
async def favicon():
    return FileResponse("static/favicon.ico")
