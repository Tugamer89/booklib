from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from securecookies import SecureCookiesMiddleware

from core.config import settings
from core.templates import templates
from routes import auth, books


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

# Gestione globale errori HTTPException
@app.exception_handler(HTTPException)
async def http_exception_redirect_auth(request: Request, exc: HTTPException):
    if exc.status_code == 401:
        return RedirectResponse(url="/auth", status_code=302)
    elif exc.status_code in (400, 404, 500):
        return templates.TemplateResponse("error.html", {
            "request": request,
            "status_code": exc.status_code,
            "title": "Oops! Qualcosa è andato storto",
            "message": exc.detail if exc.detail else "Errore imprevisto"
        }, status_code=exc.status_code)
    return await http_exception_handler(request, exc)

# Favicon route
@app.get("/favicon.ico")
async def favicon():
    return FileResponse("static/favicon.ico")
