from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi_csrf_protect import CsrfProtect
from sqlalchemy.orm import Session

from core.auth import create_session, get_authenticated_user
from core.email import send_password_reset_email, send_verification_email
from core.security import (
    generate_password_reset_token,
    generate_verification_token,
    validate_email,
    validate_password,
    validate_username_and_password,
    verify_password,
    verify_password_reset_token,
    verify_verification_token,
)
from core.templates import templates
from db.crud import (
    create_user,
    get_user_by_email,
    get_user_by_email_and_reset_token,
    get_user_by_username,
    get_user_by_username_or_email,
    logout_all,
    logout_current,
    reset_user_password,
    set_password_reset_token,
    verify_user_email,
)
from db.database import get_db
from db.models import User
from utils.logger import logger

RESET_PASSWORD_PAGE = "reset_password.html"
AUTH_PAGE = "auth.html"
FORGOT_PASSWORD_PAGE = "forgot_password.html"

router = APIRouter()


@router.get("/auth", response_class=HTMLResponse)
@router.head("/auth", response_class=HTMLResponse)
def auth_page(
    request: Request, db: Session = Depends(get_db), csrf_protect: CsrfProtect = Depends()
):
    try:
        get_authenticated_user(request, db)
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    except HTTPException:
        csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
        response = templates.TemplateResponse(
            AUTH_PAGE, {"request": request, "msg": None, "error": None, "csrf_token": csrf_token}
        )
        csrf_protect.set_csrf_cookie(signed_token, response)
        return response


def _handle_login(db: Session, username: str, password: str) -> tuple[User | None, str | None]:
    user = get_user_by_username_or_email(db, username)
    if not user or not verify_password(password, user.password):
        return None, "Credenziali errate"
    if not user.is_verified:
        return None, "Account non verificato. Controlla la tua email per il link di verifica."
    return user, None


def _handle_register(
    db: Session, username: str, password: str, email: str, request: Request
) -> tuple[str | None, str | None]:
    try:
        validate_username_and_password(username, password)
        validate_email(email)
    except HTTPException as e:
        return None, e.detail

    if get_user_by_username(db, username):
        return None, "Username già in uso"
    if get_user_by_email(db, email):
        return None, "Email già in uso"

    verification_token = generate_verification_token(email)
    user_data = {"username": username, "password": password, "email": email}
    created_user = create_user(db, user_data, verification_token)

    if not created_user:
        return None, "Errore durante la creazione dell'utente. Riprova."

    base_url = str(request.base_url).rstrip("/")
    email_sent = send_verification_email(
        created_user.email, created_user.username, verification_token, base_url
    )

    if email_sent:
        msg = "Registrazione completata! Controlla la tua email per verificare l'account."
    else:
        logger.error(f"Fallito invio email verifica a {created_user.email} dopo registrazione.")
        msg = "Registrazione completata, ma c'è stato un problema nell'invio dell'email di verifica. Contatta l'assistenza se necessario."

    return msg, None


@router.post("/auth")
async def auth_auction_post(
    request: Request,
    db: Session = Depends(get_db),
    csrf_protect: CsrfProtect = Depends(),
    auth_action: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    email: str = Form(None),
    remember_me: bool = Form(False),
):
    await csrf_protect.validate_csrf(request)

    error = None
    msg = None
    user = None
    clean_username = username.strip()
    clean_email = email.strip().lower() if email else None

    if auth_action == "login":
        user, error = _handle_login(db, clean_username, password)
    elif auth_action == "register":
        if not clean_email:
            error = "L'email è obbligatoria per la registrazione."
        else:
            msg, error = _handle_register(db, clean_username, password, clean_email, request)
    else:
        error = "Azione non valida"

    if error or msg:
        csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
        status_code = status.HTTP_400_BAD_REQUEST if error else status.HTTP_200_OK
        response = templates.TemplateResponse(
            AUTH_PAGE,
            {"request": request, "error": error, "msg": msg, "csrf_token": csrf_token},
            status_code=status_code,
        )
        csrf_protect.set_csrf_cookie(signed_token, response)
        return response

    if not user:
        error = "Si è verificato un errore imprevisto."
        csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
        response = templates.TemplateResponse(
            AUTH_PAGE,
            {
                "request": request,
                "error": error,
                "csrf_token": csrf_token,
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
        csrf_protect.set_csrf_cookie(signed_token, response)
        return response

    token = create_session(db, user.id, remember_me=remember_me)
    if not token:
        error = "Impossibile creare la sessione. Riprova."
        csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
        response = templates.TemplateResponse(
            AUTH_PAGE,
            {
                "request": request,
                "error": error,
                "csrf_token": csrf_token,
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
        csrf_protect.set_csrf_cookie(signed_token, response)
        return response

    request.session.update({"user_id": user.id, "session_token": token, "remember_me": remember_me})

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/verify-email", response_class=HTMLResponse)
async def verify_email_route(
    request: Request,
    db: Session = Depends(get_db),
    csrf_protect: CsrfProtect = Depends(),
    token: str = Query(...),
):
    email = verify_verification_token(token)
    error = None
    msg = None

    if not email:
        error = "Link di verifica non valido o scaduto."
    else:
        user = verify_user_email(db, token)
        if user:
            if user.email.lower() == email.lower():
                msg = "Account verificato con successo! Ora puoi accedere."
            else:
                logger.error(
                    f"Mismatch email nel token di verifica! Token: {token[:5]}..., Email Token: {email}, Email Utente: {user.email}"
                )
                error = "Errore durante la verifica. Contatta l'assistenza."
        else:
            existing_user = get_user_by_email(db, email)
            if existing_user and existing_user.is_verified:
                msg = "Questo account è già stato verificato. Puoi accedere."
            else:
                error = "Link di verifica non valido o già utilizzato."

    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    response = templates.TemplateResponse(
        AUTH_PAGE, {"request": request, "msg": msg, "error": error, "csrf_token": csrf_token}
    )
    csrf_protect.set_csrf_cookie(signed_token, response)
    return response


@router.get("/forgot-password", response_class=HTMLResponse)
def forgot_password_page(
    request: Request, db: Session = Depends(get_db), csrf_protect: CsrfProtect = Depends()
):
    try:
        get_authenticated_user(request, db)
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    except HTTPException:
        csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
        response = templates.TemplateResponse(
            FORGOT_PASSWORD_PAGE,
            {"request": request, "msg": None, "error": None, "csrf_token": csrf_token},
        )
        csrf_protect.set_csrf_cookie(signed_token, response)
        return response


@router.post("/forgot-password")
async def handle_forgot_password(
    request: Request,
    db: Session = Depends(get_db),
    csrf_protect: CsrfProtect = Depends(),
    email: str = Form(...),
):
    await csrf_protect.validate_csrf(request)

    user = get_user_by_email(db, email.strip().lower())
    msg = "Se un account con questa email esiste, abbiamo inviato un link per il reset della password."

    if user:
        token = generate_password_reset_token(user.email)
        if not set_password_reset_token(db, user, token):
            logger.error(f"Fallito salvataggio reset token DB per {user.email}")
        else:
            base_url = str(request.base_url).rstrip("/")
            email_sent = send_password_reset_email(user.email, user.username, token, base_url)
            if not email_sent:
                logger.warning(f"Tentativo invio email reset per {user.email} fallito.")

    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    response = templates.TemplateResponse(
        FORGOT_PASSWORD_PAGE, {"request": request, "msg": msg, "csrf_token": csrf_token}
    )
    csrf_protect.set_csrf_cookie(signed_token, response)
    return response


@router.get("/reset-password", response_class=HTMLResponse)
def reset_password_page(
    request: Request,
    db: Session = Depends(get_db),
    csrf_protect: CsrfProtect = Depends(),
    token: str = Query(...),
):
    email = verify_password_reset_token(token)
    error = "Link di reset non valido o scaduto. Richiedine uno nuovo."

    if not email:
        csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
        response = templates.TemplateResponse(
            FORGOT_PASSWORD_PAGE, {"request": request, "error": error, "csrf_token": csrf_token}
        )
        csrf_protect.set_csrf_cookie(signed_token, response)
        return response

    user = get_user_by_email_and_reset_token(db, email, token)
    if not user:
        csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
        response = templates.TemplateResponse(
            FORGOT_PASSWORD_PAGE, {"request": request, "error": error, "csrf_token": csrf_token}
        )
        csrf_protect.set_csrf_cookie(signed_token, response)
        return response

    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    response = templates.TemplateResponse(
        RESET_PASSWORD_PAGE,
        {"request": request, "token": token, "error": None, "msg": None, "csrf_token": csrf_token},
    )
    csrf_protect.set_csrf_cookie(signed_token, response)
    return response


@router.post("/reset-password")
async def handle_reset_password(
    request: Request,
    db: Session = Depends(get_db),
    csrf_protect: CsrfProtect = Depends(),
    token: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
):
    await csrf_protect.validate_csrf(request)

    error = None
    if password != confirm_password:
        error = "Le password non coincidono."
    else:
        try:
            validate_password(password)
        except HTTPException as e:
            error = e.detail

    if error:
        csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
        response = templates.TemplateResponse(
            RESET_PASSWORD_PAGE,
            {
                "request": request,
                "token": token,
                "error": error,
                "msg": None,
                "csrf_token": csrf_token,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )
        csrf_protect.set_csrf_cookie(signed_token, response)
        return response

    email = verify_password_reset_token(token)
    if not email:
        error = "Link di reset non valido o scaduto. Richiedine uno nuovo."
        csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
        response = templates.TemplateResponse(
            FORGOT_PASSWORD_PAGE, {"request": request, "error": error, "csrf_token": csrf_token}
        )
        csrf_protect.set_csrf_cookie(signed_token, response)
        return response

    user = get_user_by_email_and_reset_token(db, email, token)

    if not user:
        error = "Link di reset non valido o scaduto (utente non trovato o token non corrispondente). Richiedine uno nuovo."
        csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
        response = templates.TemplateResponse(
            FORGOT_PASSWORD_PAGE, {"request": request, "error": error, "csrf_token": csrf_token}
        )
        csrf_protect.set_csrf_cookie(signed_token, response)
        return response

    if not reset_user_password(db, user, password):
        error = "Errore interno durante l'aggiornamento della password. Riprova."
        csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
        response = templates.TemplateResponse(
            RESET_PASSWORD_PAGE,
            {
                "request": request,
                "token": token,
                "error": error,
                "msg": None,
                "csrf_token": csrf_token,
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
        csrf_protect.set_csrf_cookie(signed_token, response)
        return response

    logout_all(db, user.id)
    request.session.clear()

    msg = "Password aggiornata con successo. Ora puoi accedere."
    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    response = templates.TemplateResponse(
        AUTH_PAGE, {"request": request, "msg": msg, "error": None, "csrf_token": csrf_token}
    )
    csrf_protect.set_csrf_cookie(signed_token, response)
    return response


@router.get("/logout")
def logout(
    request: Request,
    user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db),
    csrf_protect: CsrfProtect = Depends(),
):
    token = request.session.get("session_token")
    if token:
        logout_current(db, token)

    request.session.clear()

    response = RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    response.delete_cookie("session")
    response.delete_cookie("fastapi-csrf-token")

    csrf_protect.unset_csrf_cookie(response)
    return response
