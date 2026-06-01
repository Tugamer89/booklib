from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request, status
from fastapi.concurrency import run_in_threadpool
from fastapi_csrf_protect import CsrfProtect
from sqlalchemy.orm import Session

from core.auth import admin_required
from core.config import settings
from core.email import send_password_reset_email
from core.security import generate_password_reset_token
from core.templates import templates
from db.crud import set_password_reset_token
from db.database import get_db
from db.models import User
from utils.logger import logger

ADMIN_USERS_PAGE = "admin_users.html"

router = APIRouter()


@router.get("/admin/users")
def admin_users_list(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    csrf_protect: Annotated[CsrfProtect, Depends()],
    admin: Annotated[User, Depends(admin_required)],
    msg: Annotated[str | None, Query()] = None,
    error: Annotated[str | None, Query()] = None,
):
    users = db.query(User).order_by(User.id).all()

    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    response = templates.TemplateResponse(
        request=request,
        name=ADMIN_USERS_PAGE,
        context={"users": users, "msg": msg, "error": error, "csrf_token": csrf_token},
    )
    csrf_protect.set_csrf_cookie(signed_token, response)
    return response


@router.post("/admin/users/reset-password")
async def admin_reset_password(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    csrf_protect: Annotated[CsrfProtect, Depends()],
    admin: Annotated[User, Depends(admin_required)],
    user_id: Annotated[int, Form(...)],
):
    await csrf_protect.validate_csrf(request)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    token = generate_password_reset_token(user.email)
    if not set_password_reset_token(db, user, token):
        logger.error(f"Failed to save reset token to DB for {user.email} triggered by admin")
        msg, error = "", "Failed to generate reset token. Internal error."
    else:
        base_url = (
            settings.app_base_url.rstrip("/")
            if settings.app_base_url
            else str(request.base_url).rstrip("/")
        )
        # Offload synchronous blocking I/O operation to prevent blocking the asyncio event loop
        email_sent = await run_in_threadpool(
            send_password_reset_email, user.email, user.username, token, base_url
        )

        if email_sent:
            msg, error = f"Password reset link sent to {user.email}", ""
        else:
            msg, error = "", f"Failed to send email to {user.email}. Check SMTP settings."

    users = db.query(User).order_by(User.id).all()
    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    response = templates.TemplateResponse(
        request=request,
        name=ADMIN_USERS_PAGE,
        context={
            "users": users,
            "msg": msg,
            "error": error,
            "csrf_token": csrf_token,
        },
    )
    csrf_protect.set_csrf_cookie(signed_token, response)
    return response


@router.post("/admin/users/delete")
async def admin_delete_user(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    csrf_protect: Annotated[CsrfProtect, Depends()],
    admin: Annotated[User, Depends(admin_required)],
    user_id: Annotated[int, Form(...)],
):
    await csrf_protect.validate_csrf(request)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user_id == admin.id:
        users = db.query(User).order_by(User.id).all()
        csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
        response = templates.TemplateResponse(
            request=request,
            name=ADMIN_USERS_PAGE,
            context={
                "users": users,
                "msg": "",
                "error": "You cannot delete yourself.",
                "csrf_token": csrf_token,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )
        csrf_protect.set_csrf_cookie(signed_token, response)
        return response

    db.delete(user)
    db.commit()

    users = db.query(User).order_by(User.id).all()
    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    response = templates.TemplateResponse(
        request=request,
        name=ADMIN_USERS_PAGE,
        context={
            "users": users,
            "msg": "User deleted",
            "error": "",
            "csrf_token": csrf_token,
        },
    )
    csrf_protect.set_csrf_cookie(signed_token, response)
    return response
