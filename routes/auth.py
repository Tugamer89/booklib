from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi_csrf_protect.exceptions import TokenValidationError
from passlib.hash import bcrypt
from sqlalchemy.orm import Session

from core.auth import get_authenticated_user, create_session
from core.security import validate_credentials
from db.crud import get_user_by_username, logout_current
from db.database import get_db
from db.models import User

router = APIRouter()


@router.get("/auth", response_class=HTMLResponse)
@router.head("/auth", response_class=HTMLResponse)
def auth_page(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        get_authenticated_user(request, db)
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    except HTTPException:
        from fastapi.templating import Jinja2Templates
        templates = Jinja2Templates(directory="templates")
        return templates.TemplateResponse("auth.html", {"request": request})


@router.post("/auth")
async def auth_action(
    request: Request,
    db: Session = Depends(get_db),
    username: str = Form(...),
    password: str = Form(...),
    authAction: str = Form(...)
):
    error = None
    user = None
    clean_username = username.strip()

    if authAction == "login":
        user = get_user_by_username(db, clean_username)
        if not user or not bcrypt.verify(password, user.password):
            error = "Credenziali errate"
    elif authAction == "register":
        try:
            validate_credentials(clean_username, password)
        except HTTPException as e:
            error = e.detail
        if not error and get_user_by_username(db, clean_username):
            error = "Username già in uso"
        if not error:
            user = User(username=clean_username, password=bcrypt.hash(password))
            db.add(user)
            db.commit()
    else:
        error = "Azione non valida"

    if error or not user:
        return RedirectResponse(
            url=f"/auth?error={error}",
            status_code=status.HTTP_303_SEE_OTHER
        )

    token = create_session(db, user.id)
    request.session["user_id"] = user.id
    request.session["session_token"] = token
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


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