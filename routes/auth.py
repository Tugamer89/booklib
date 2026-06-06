from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request, status
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi_csrf_protect import CsrfProtect
from sqlalchemy.orm import Session

from core.auth import create_session, get_authenticated_user
from core.config import settings
from core.email import send_password_reset_email, send_verification_email
from core.limiter import limiter
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
    check_user_exists,
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
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    csrf_protect: Annotated[CsrfProtect, Depends()],
):
    try:
        get_authenticated_user(request, db)
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    except HTTPException:
        csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
        response = templates.TemplateResponse(
            request=request,
            name=AUTH_PAGE,
            context={"msg": None, "error": None, "csrf_token": csrf_token},
        )
        csrf_protect.set_csrf_cookie(signed_token, response)
        return response


def _handle_login(db: Session, username: str, password: str) -> tuple[User | None, str | None]:
    user = get_user_by_username_or_email(db, username)
    if not user or not verify_password(password, user.password):
        return None, "Invalid credentials"
    if not user.is_verified:
        return None, "Account not verified. Check your email for the verification link."
    return user, None


async def _handle_register(
    db: Session, username: str, password: str, email: str, request: Request
) -> tuple[str | None, str | None]:
    try:
        validate_username_and_password(username, password)
        validate_email(email)
    except HTTPException as e:
        return None, e.detail

    username_exists, email_exists = check_user_exists(db, username, email)
    if username_exists:
        return None, "Username already in use"
    if email_exists:
        return None, "Email already in use"

    verification_token = generate_verification_token(email)
    user_data = {"username": username, "password": password, "email": email}
    created_user = create_user(db, user_data, verification_token)

    if not created_user:
        return None, "Error creating user. Please try again."

    base_url = (
        settings.app_base_url.rstrip("/")
        if settings.app_base_url
        else str(request.base_url).rstrip("/")
    )
    # Offload synchronous blocking I/O operation to prevent blocking the asyncio event loop
    email_sent = await run_in_threadpool(
        send_verification_email,
        created_user.email,
        created_user.username,
        verification_token,
        base_url,
    )

    if email_sent:
        msg = "Registration complete! Check your email to verify your account."
    else:
        logger.error(
            f"Failed to send verification email to {created_user.email} after registration."
        )
        msg = "Registration complete, but there was a problem sending the verification email. Please contact support if needed."

    return msg, None


@router.post("/auth")
@limiter.limit("5/minute")
async def auth_auction_post(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    csrf_protect: Annotated[CsrfProtect, Depends()],
    auth_action: Annotated[str, Form(...)],
    username: Annotated[str, Form(...)],
    password: Annotated[str, Form(...)],
    email: Annotated[str | None, Form()] = None,
    remember_me: Annotated[bool, Form()] = False,
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
            error = "Email is required for registration."
        else:
            msg, error = await _handle_register(db, clean_username, password, clean_email, request)
    else:
        error = "Invalid action"

    if error or msg:
        csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
        status_code = status.HTTP_400_BAD_REQUEST if error else status.HTTP_200_OK
        response = templates.TemplateResponse(
            request=request,
            name=AUTH_PAGE,
            context={"error": error, "msg": msg, "csrf_token": csrf_token},
            status_code=status_code,
        )
        csrf_protect.set_csrf_cookie(signed_token, response)
        return response

    if not user:
        error = "An unexpected error occurred."
        csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
        response = templates.TemplateResponse(
            request=request,
            name=AUTH_PAGE,
            context={
                "error": error,
                "csrf_token": csrf_token,
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
        csrf_protect.set_csrf_cookie(signed_token, response)
        return response

    token = create_session(db, user.id, remember_me=remember_me)
    if not token:
        error = "Unable to create session. Please try again."
        csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
        response = templates.TemplateResponse(
            request=request,
            name=AUTH_PAGE,
            context={
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
    db: Annotated[Session, Depends(get_db)],
    csrf_protect: Annotated[CsrfProtect, Depends()],
    token: Annotated[str, Query(...)],
):
    email = verify_verification_token(token)
    error = None
    msg = None

    if not email:
        error = "Invalid or expired verification link."
    else:
        user = verify_user_email(db, token)
        if user:
            if user.email.lower() == email.lower():
                msg = "Account verified successfully! You can now log in."
            else:
                logger.error(
                    f"Email mismatch in verification token! Token: {token[:5]}..., Token Email: {email}, User Email: {user.email}"
                )
                error = "Verification error. Please contact support."
        else:
            existing_user = get_user_by_email(db, email)
            if existing_user and existing_user.is_verified:
                msg = "This account has already been verified. You can log in."
            else:
                error = "Invalid or already used verification link."

    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    response = templates.TemplateResponse(
        request=request,
        name=AUTH_PAGE,
        context={"msg": msg, "error": error, "csrf_token": csrf_token},
    )
    csrf_protect.set_csrf_cookie(signed_token, response)
    return response


@router.get("/forgot-password", response_class=HTMLResponse)
def forgot_password_page(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    csrf_protect: Annotated[CsrfProtect, Depends()],
):
    try:
        get_authenticated_user(request, db)
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    except HTTPException:
        csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
        response = templates.TemplateResponse(
            request=request,
            name=FORGOT_PASSWORD_PAGE,
            context={"msg": None, "error": None, "csrf_token": csrf_token},
        )
        csrf_protect.set_csrf_cookie(signed_token, response)
        return response


@router.post("/forgot-password")
@limiter.limit("3/minute")
async def handle_forgot_password(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    csrf_protect: Annotated[CsrfProtect, Depends()],
    email: Annotated[str, Form(...)],
):
    await csrf_protect.validate_csrf(request)

    user = get_user_by_email(db, email.strip().lower())
    msg = "If an account with this email exists, we have sent a password reset link."

    if user:
        token = generate_password_reset_token(user.email)
        if not set_password_reset_token(db, user, token):
            logger.error(f"Failed to save reset token to DB for {user.email}")
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
            if not email_sent:
                logger.warning(f"Failed attempt to send reset email for {user.email}.")

    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    response = templates.TemplateResponse(
        request=request, name=FORGOT_PASSWORD_PAGE, context={"msg": msg, "csrf_token": csrf_token}
    )
    csrf_protect.set_csrf_cookie(signed_token, response)
    return response


@router.get("/reset-password", response_class=HTMLResponse)
def reset_password_page(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    csrf_protect: Annotated[CsrfProtect, Depends()],
    token: Annotated[str, Query(...)],
):
    email = verify_password_reset_token(token)
    error = "Invalid or expired reset link. Please request a new one."

    if not email:
        csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
        response = templates.TemplateResponse(
            request=request,
            name=FORGOT_PASSWORD_PAGE,
            context={"error": error, "csrf_token": csrf_token},
        )
        csrf_protect.set_csrf_cookie(signed_token, response)
        return response

    user = get_user_by_email_and_reset_token(db, email, token)
    if not user:
        csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
        response = templates.TemplateResponse(
            request=request,
            name=FORGOT_PASSWORD_PAGE,
            context={"error": error, "csrf_token": csrf_token},
        )
        csrf_protect.set_csrf_cookie(signed_token, response)
        return response

    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    response = templates.TemplateResponse(
        request=request,
        name=RESET_PASSWORD_PAGE,
        context={"token": token, "error": None, "msg": None, "csrf_token": csrf_token},
    )
    csrf_protect.set_csrf_cookie(signed_token, response)
    return response


@router.post("/reset-password")
@limiter.limit("3/minute")
async def handle_reset_password(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    csrf_protect: Annotated[CsrfProtect, Depends()],
    token: Annotated[str, Form(...)],
    password: Annotated[str, Form(...)],
    confirm_password: Annotated[str, Form(...)],
):
    await csrf_protect.validate_csrf(request)

    error = None
    if password != confirm_password:
        error = "Passwords do not match."
    else:
        try:
            validate_password(password)
        except HTTPException as e:
            error = e.detail

    if error:
        csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
        response = templates.TemplateResponse(
            request=request,
            name=RESET_PASSWORD_PAGE,
            context={
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
        error = "Invalid or expired reset link. Please request a new one."
        csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
        response = templates.TemplateResponse(
            request=request,
            name=FORGOT_PASSWORD_PAGE,
            context={"error": error, "csrf_token": csrf_token},
        )
        csrf_protect.set_csrf_cookie(signed_token, response)
        return response

    user = get_user_by_email_and_reset_token(db, email, token)

    if not user:
        error = "Invalid or expired reset link (user not found or token mismatch). Please request a new one."
        csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
        response = templates.TemplateResponse(
            request=request,
            name=FORGOT_PASSWORD_PAGE,
            context={"error": error, "csrf_token": csrf_token},
        )
        csrf_protect.set_csrf_cookie(signed_token, response)
        return response

    if not reset_user_password(db, user, password):
        error = "Internal error while updating the password. Please try again."
        csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
        response = templates.TemplateResponse(
            request=request,
            name=RESET_PASSWORD_PAGE,
            context={
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

    msg = "Password updated successfully. You can now log in."
    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    response = templates.TemplateResponse(
        request=request,
        name=AUTH_PAGE,
        context={"msg": msg, "error": None, "csrf_token": csrf_token},
    )
    csrf_protect.set_csrf_cookie(signed_token, response)
    return response


@router.get("/logout")
def logout(
    request: Request,
    user: Annotated[User, Depends(get_authenticated_user)],
    db: Annotated[Session, Depends(get_db)],
    csrf_protect: Annotated[CsrfProtect, Depends()],
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
