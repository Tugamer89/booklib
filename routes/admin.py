from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from passlib.hash import bcrypt

from core.auth import admin_required
from core.config import settings
from core.templates import templates
from db.database import get_db
from db.models import User

router = APIRouter()

@router.get("/admin/users")
def admin_users_list(
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(admin_required),
    msg: str = Query(None),
    error: str = Query(None)
):
    users = db.query(User).order_by(User.id).all()
    return templates.TemplateResponse("admin_users.html", {
        "request": request,
        "users": users,
        "msg": msg,
        "error": error
    })

@router.post("/admin/users/reset-password")
async def admin_reset_password(
    request: Request,
    user_id: int = Form(...),
    new_password: str = Form(...),
    db: Session = Depends(get_db),
    admin = Depends(admin_required)
):
    if len(new_password) < 8:
        return admin_users_list(
            request=request,
            db=db,
            admin=admin,
            msg="",
            error="Password troppo corta"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utente non trovato")
    
    user.password = bcrypt.hash(new_password)
    db.commit()
    return admin_users_list(
        request=request,
        db=db,
        admin=admin,
        msg="Password aggiornata",
        error=''
    )

@router.post("/admin/users/delete")
async def admin_delete_user(
    request: Request,
    user_id: int = Form(...),
    db: Session = Depends(get_db),
    admin = Depends(admin_required)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utente non trovato")
    
    db.delete(user)
    db.commit()
    return admin_users_list(
        request=request,
        db=db,
        admin=admin,
        msg="Utente eliminato",
        error=""
    )
