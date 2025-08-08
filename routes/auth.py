import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi_csrf_protect.exceptions import TokenValidationError
from passlib.hash import bcrypt
from sqlalchemy.orm import Session

from core.auth import get_authenticated_user
from core.csrf import CsrfProtect
from core.security import validate_credentials
from core.templates import templates
from db.crud import get_user_by_username
from db.database import get_db
from db.models import User


router = APIRouter()


@router.get("/auth", response_class=HTMLResponse)
def auth_page(
    request: Request,
    db: Session = Depends(get_db),
    error: str = Query(None),
    username: str = Query(None),
    csrf_protect: CsrfProtect = Depends()
):
    try:
        get_authenticated_user(request, db)
        return RedirectResponse("/", status_code=302)
    except HTTPException:
        pass

    raw_token, signed_token = csrf_protect.generate_csrf_tokens()
    response = templates.TemplateResponse("auth.html", {
        "request": request,
        "error": error,
        "username": username or "",
        "csrf_token": raw_token
    })
    response.set_cookie(
        key=csrf_protect._cookie_key,
        value=signed_token,
        httponly=True,
        secure=csrf_protect._cookie_secure,
        samesite=csrf_protect._cookie_samesite,
        max_age=csrf_protect._max_age
    )
    return response


@router.post("/auth")
async def auth_action(
    request: Request,
    db: Session = Depends(get_db),
    username: str = Form(...),
    password: str = Form(...),
    authAction: str = Form(...),
    csrf_protect: CsrfProtect = Depends()
):
    error = None
    user = None

    try:
        await csrf_protect.validate_csrf(request)
    except TokenValidationError:
        error = "Token CSRF non valido"
    else:
        if authAction == "login":
            user = get_user_by_username(db, username)
            if not user or not bcrypt.verify(password, user.password):
                error = "Credenziali errate"
        elif authAction == "register":
            try:
                validate_credentials(username, password)
            except HTTPException as e:
                error = e.detail
            if get_user_by_username(db, username):
                error = "Username già in uso"
                username = ""
            if not error:
                user = User(username=username, password=bcrypt.hash(password))
                db.add(user)
                db.commit()
        else:
            error = "Azione non valida"

    if error or not user:
        return auth_page(
            request=request,
            db=db,
            error=error,
            username=username,
            csrf_protect=csrf_protect
        )


    token = secrets.token_hex(32)
    expiry = datetime.now(timezone.utc) + timedelta(days=7)
    user.session_token = token
    user.session_expiry = expiry
    db.commit()

    request.session["user_id"] = user.id
    request.session["session_token"] = token
    return RedirectResponse("/", status_code=302)


@router.get("/logout")
def logout(
    request: Request,
    user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db)
):
    user.session_token = None
    user.session_expiry = None
    db.commit()
    request.session.clear()
    return RedirectResponse("/auth", status_code=302)
