import secrets
from datetime import UTC, datetime, timedelta

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from core.config import settings
from db.crud import get_user_by_id
from db.database import get_db
from db.models import User, UserSession


def create_session(db: Session, user_id: int, remember_me: bool = False) -> str:
    active_sessions = (
        db.query(UserSession)
        .filter(UserSession.user_id == user_id, UserSession.expires_at > datetime.now(UTC))
        .count()
    )

    if active_sessions >= settings.max_sessions_per_user:
        oldest_session = (
            db.query(UserSession)
            .filter(UserSession.user_id == user_id)
            .order_by(UserSession.expires_at.asc())
            .first()
        )
        if oldest_session:
            db.delete(oldest_session)
            db.commit()

    token = secrets.token_urlsafe(32)

    if remember_me:
        expires_at = datetime.now(UTC) + timedelta(days=settings.session_cookie_max_age_days)
    else:
        expires_at = datetime.now(UTC) + timedelta(hours=8)

    session = UserSession(user_id=user_id, token=token, expires_at=expires_at)
    db.add(session)
    db.commit()
    return token


def get_authenticated_user(request: Request, db: Session = Depends(get_db)) -> User:
    user_id = request.session.get("user_id")
    session_token = request.session.get("session_token")

    if not user_id or not session_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    db_session = (
        db.query(UserSession)
        .filter(UserSession.user_id == user_id, UserSession.token == session_token)
        .first()
    )

    if not db_session:
        request.session.clear()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")

    if db_session.expires_at and db_session.expires_at < datetime.now(UTC):
        request.session.clear()
        db.delete(db_session)
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")

    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


def admin_required(user: User = Depends(get_authenticated_user)) -> User:
    if user.username not in settings.admin_users:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return user
