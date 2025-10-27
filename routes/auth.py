from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from urllib.parse import urlencode

from core.auth import get_authenticated_user, create_session
from core.security import (
    generate_password_reset_token,
    generate_verification_token,
    validate_email,
    validate_password,
    validate_username_and_password,
    verify_password_reset_token,
    verify_verification_token,
    verify_password
)
from core.email import send_password_reset_email, send_verification_email
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
    verify_user_email
)
from db.database import get_db
from db.models import User
from utils.logger import logger

router = APIRouter()


@router.get("/auth", response_class=HTMLResponse)
@router.head("/auth", response_class=HTMLResponse)
def auth_page(
    request: Request,
    db: Session = Depends(get_db),
    msg: str = Query(None),
    error: str = Query(None)
):
    try:
        get_authenticated_user(request, db)
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    except HTTPException:
        return templates.TemplateResponse("auth.html", {
            "request": request,
            "msg": msg,
            "error": error
        })


@router.post("/auth")
async def auth_action(
    request: Request,
    db: Session = Depends(get_db),
    authAction: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    email: str = Form(None)
):
    error = None
    msg = None
    user = None
    clean_username = username.strip()
    clean_email = email.strip().lower() if email else None

    if authAction == "login":
        user = get_user_by_username_or_email(db, clean_username)
        if not user or not verify_password(password, user.password):
            error = "Credenziali errate"
        elif not user.is_verified:
            error = "Account non verificato. Controlla la tua email per il link di verifica."
            user = None
    
    elif authAction == "register":
        try:
            validate_username_and_password(clean_username, password)
            validate_email(clean_email)
        except HTTPException as e:
            error = e.detail
        
        if not error and get_user_by_username(db, clean_username):
            error = "Username già in uso"
        if not error and get_user_by_email(db, clean_email):
            error = "Email già in uso"
        
        if not error:
            verification_token = generate_verification_token(clean_email)
            user_data = {
                "username": clean_username,
                "password": password,
                "email": clean_email
            }
            created_user = create_user(db, user_data, verification_token)

            if created_user:
                base_url = str(request.base_url).rstrip('/')
                email_sent = send_verification_email(
                    created_user.email, created_user.username, verification_token, base_url
                )
                
                if email_sent:
                    msg = "Registrazione completata! Controlla la tua email per verificare l'account."
                else:
                    logger.error(f"Fallito invio email verifica a {created_user.email} dopo registrazione.")
                    msg = "Registrazione completata, ma c'è stato un problema nell'invio dell'email di verifica. Contatta l'assistenza se necessario."
                    
                user = None
            else:
                error = "Errore durante la creazione dell'utente. Riprova."

    else:
        error = "Azione non valida"

    if error:
        redirect_url = f"/auth?{urlencode({'error': error})}"
        return RedirectResponse(url=redirect_url, status_code=status.HTTP_303_SEE_OTHER)

    if msg:
        redirect_url = f"/auth?{urlencode({'msg': msg})}"
        return RedirectResponse(url=redirect_url, status_code=status.HTTP_303_SEE_OTHER)

    if user and user.is_verified:
        token = create_session(db, user.id)
        if token:
            request.session["user_id"] = user.id
            request.session["session_token"] = token
            return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
        else:
            error = "Impossibile creare la sessione. Riprova."
            redirect_url = f"/auth?{urlencode({'error': error})}"
            return RedirectResponse(url=redirect_url, status_code=status.HTTP_303_SEE_OTHER)

    error = "Si è verificato un errore imprevisto."
    redirect_url = f"/auth?{urlencode({'error': error})}"
    return RedirectResponse(url=redirect_url, status_code=status.HTTP_303_SEE_OTHER)


@router.get("/verify-email", response_class=HTMLResponse)
async def verify_email_route(
    request: Request,
    db: Session = Depends(get_db),
    token: str = Query(...)
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
                logger.error(f"Mismatch email nel token di verifica! Token: {token[:5]}..., Email Token: {email}, Email Utente: {user.email}")
                error = "Errore durante la verifica. Contatta l'assistenza."
        else:
            existing_user = get_user_by_email(db, email)
            if existing_user and existing_user.is_verified:
                msg = "Questo account è già stato verificato. Puoi accedere."
            else:
                error = "Link di verifica non valido o già utilizzato."

    query_params = {}
    if msg:
        query_params['msg'] = msg
    if error:
        query_params['error'] = error

    redirect_url = f"/auth?{urlencode(query_params)}"
    return RedirectResponse(url=redirect_url, status_code=status.HTTP_303_SEE_OTHER)


@router.get("/forgot-password", response_class=HTMLResponse)
def forgot_password_page(
    request: Request,
    db: Session = Depends(get_db),
    msg: str = Query(None),
    error: str = Query(None)
):
    try:
        get_authenticated_user(request, db)
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    except HTTPException:
        return templates.TemplateResponse("forgot_password.html", {
            "request": request,
            "msg": msg,
            "error": error
        })


@router.post("/forgot-password")
async def handle_forgot_password(
    request: Request,
    db: Session = Depends(get_db),
    email: str = Form(...)
):
    user = get_user_by_email(db, email.strip().lower())
    msg = "Se un account con questa email esiste, abbiamo inviato un link per il reset della password."
    
    if user:
        token = generate_password_reset_token(user.email)
        if not set_password_reset_token(db, user, token):
            logger.error(f"Fallito salvataggio reset token DB per {user.email}")
        else:
            base_url = str(request.base_url).rstrip('/')
            email_sent = send_password_reset_email(user.email, user.username, token, base_url)
            if not email_sent:
                logger.warning(f"Tentativo invio email reset per {user.email} fallito.")

    return RedirectResponse(
        url=f"/forgot-password?{urlencode({'msg': msg})}",
        status_code=status.HTTP_303_SEE_OTHER
    )


@router.get("/reset-password", response_class=HTMLResponse)
def reset_password_page(
    request: Request,
    db: Session = Depends(get_db),
    token: str = Query(...)
):
    email = verify_password_reset_token(token)
    
    if not email:
        error = "Link di reset non valido o scaduto. Richiedine uno nuovo."
        return RedirectResponse(
            url=f"/forgot-password?{urlencode({'error': error})}",
            status_code=status.HTTP_303_SEE_OTHER
        )
    
    user = get_user_by_email_and_reset_token(db, email, token)
    if not user:
        error = "Link di reset non valido o scaduto. Richiedine uno nuovo."
        return RedirectResponse(
            url=f"/forgot-password?{urlencode({'error': error})}",
            status_code=status.HTTP_303_SEE_OTHER
        )
    
    return templates.TemplateResponse("reset_password.html", {
        "request": request,
        "token": token,
        "error": None,
        "msg": None
    })


@router.post("/reset-password")
async def handle_reset_password(
    request: Request,
    db: Session = Depends(get_db),
    token: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    error = None
    if password != confirm_password:
        error = "Le password non coincidono."
    else:
        try:
            validate_password(password)
        except HTTPException as e:
            error = e.detail

    if error:
        return templates.TemplateResponse("reset_password.html", {
            "request": request,
            "token": token,
            "error": error,
            "msg": None
        }, status_code=status.HTTP_400_BAD_REQUEST)

    email = verify_password_reset_token(token)
    if not email:
        error="Link di reset non valido o scaduto. Richiedine uno nuovo."
        return RedirectResponse(
            url=f"/forgot-password?{urlencode({'error': error})}",
            status_code=status.HTTP_303_SEE_OTHER
        )

    user = get_user_by_email_and_reset_token(db, email, token)
    
    if not user:
        error="Link di reset non valido o scaduto (utente non trovato o token non corrispondente). Richiedine uno nuovo."
        return RedirectResponse(
            url=f"/forgot-password?{urlencode({'error': error})}",
            status_code=status.HTTP_303_SEE_OTHER
        )

    if not reset_user_password(db, user, password):
        error = "Errore interno durante l'aggiornamento della password. Riprova."
        return templates.TemplateResponse("reset_password.html", {
            "request": request,
            "token": token,
            "error": error,
            "msg": None
        }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    logout_all(db, user.id)
    request.session.clear()

    msg = "Password aggiornata con successo. Ora puoi accedere."
    return RedirectResponse(
        url=f"/auth?{urlencode({'msg': msg})}",
        status_code=status.HTTP_303_SEE_OTHER
    )


@router.get("/logout")
def logout(
    request: Request,
    user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db)
):
    token = request.session.get("session_token")
    if token:
        logout_current(db, token)
    request.session.clear()
    return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
