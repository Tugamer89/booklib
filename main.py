from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from securecookies import SecureCookiesMiddleware

from db.database import engine, Base
from core.config import settings
from core.templates import templates
from routes import auth, books, debug


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

app.include_router(auth.router)
app.include_router(books.router)
if settings.DEBUG:
    app.include_router(debug.router)

@app.on_event("startup")
async def on_startup():
    Base.metadata.create_all(bind=engine)

# Gestione HTTPException
@app.exception_handler(StarletteHTTPException)
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
@app.exception_handler(RequestValidationError)
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

# Gestione eccezioni generiche (qualsiasi errore non catturato sopra)
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    # Log dell'errore vero per debugging
    import traceback
    print("ERRORE GENERICO:", "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)))

    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "status_code": 500,
            "title": "Errore interno",
            "message": "Si è verificato un errore imprevisto. Riprova più tardi."
        },
        status_code=500
    )

# Favicon route
@app.get("/favicon.ico")
async def favicon():
    return FileResponse("static/favicon.ico")
