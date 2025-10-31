from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request, status
from fastapi_csrf_protect import CsrfProtect
from sqlalchemy.orm import Session

from core.auth import admin_required
from core.templates import templates
from core.security import hash_password
from db.crud import logout_all
from db.database import get_db
from db.models import User

ADMIN_USERS_PAGE = "admin_users.html"

router = APIRouter()

@router.get("/admin/users")
def admin_users_list(
    request: Request,
    db: Session = Depends(get_db),
    csrf_protect: CsrfProtect = Depends(),
    admin: User = Depends(admin_required),
    msg: str = Query(None),
    error: str = Query(None)
):
    users = db.query(User).order_by(User.id).all()
    
    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    response = templates.TemplateResponse(ADMIN_USERS_PAGE, {
        "request": request,
        "users": users,
        "msg": msg,
        "error": error,
        "csrf_token": csrf_token
    })
    csrf_protect.set_csrf_cookie(signed_token, response)
    return response

@router.post("/admin/users/reset-password")
async def admin_reset_password(
    request: Request,
    db: Session = Depends(get_db),
    csrf_protect: CsrfProtect = Depends(),
    admin = Depends(admin_required),
    user_id: int = Form(...),
    new_password: str = Form(...)
):
    await csrf_protect.validate_csrf(request)
    
    if len(new_password) < 8:
        users = db.query(User).order_by(User.id).all()
        csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
        response = templates.TemplateResponse(ADMIN_USERS_PAGE, {
            "request": request,
            "users": users,
            "msg": "",
            "error": "Password troppo corta",
            "csrf_token": csrf_token
        }, status_code=status.HTTP_400_BAD_REQUEST)
        csrf_protect.set_csrf_cookie(signed_token, response)
        return response

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utente non trovato")
    
    user.password = hash_password(new_password)
    db.commit()
    logout_all(db, user_id)
    
    users = db.query(User).order_by(User.id).all()
    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    response = templates.TemplateResponse(ADMIN_USERS_PAGE, {
        "request": request,
        "users": users,
        "msg": "Password aggiornata",
        "error": "",
        "csrf_token": csrf_token
    })
    csrf_protect.set_csrf_cookie(signed_token, response)
    return response

@router.post("/admin/users/delete")
async def admin_delete_user(
    request: Request,
    db: Session = Depends(get_db),
    csrf_protect: CsrfProtect = Depends(),
    admin = Depends(admin_required),
    user_id: int = Form(...)
):
    await csrf_protect.validate_csrf(request)
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utente non trovato")
    
    if user_id == admin.id:
        users = db.query(User).order_by(User.id).all()
        csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
        response = templates.TemplateResponse(ADMIN_USERS_PAGE, {
            "request": request,
            "users": users,
            "msg": "",
            "error": "Non puoi eliminare te stesso.",
            "csrf_token": csrf_token
        }, status_code=status.HTTP_400_BAD_REQUEST)
        csrf_protect.set_csrf_cookie(signed_token, response)
        return response
    
    db.delete(user)
    db.commit()
    
    users = db.query(User).order_by(User.id).all()
    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    response = templates.TemplateResponse(ADMIN_USERS_PAGE, {
        "request": request,
        "users": users,
        "msg": "Utente eliminato",
        "error": "",
        "csrf_token": csrf_token
    })
    csrf_protect.set_csrf_cookie(signed_token, response)
    return response
