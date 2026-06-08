from datetime import UTC, datetime, timedelta

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from core.config import settings
from core.security import hash_password
from db.models import Book, User, UserSession
from utils.logger import logger


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_user_by_username_or_email(db: Session, identifier: str) -> User | None:
    identifier_lower = identifier.lower()

    # Optimize DB hits by checking both username and email in a single query
    return (
        db.query(User)
        .filter(or_(User.email == identifier_lower, func.lower(User.username) == identifier_lower))
        .first()
    )


def check_user_exists(db: Session, username: str, email: str) -> tuple[bool, bool]:
    """
    Checks if a user exists with the given username or email in a single query.
    Returns a tuple of (username_exists, email_exists).
    """
    user = db.query(User).filter(or_(User.username == username, User.email == email)).first()
    if not user:
        return False, False
    return user.username == username, user.email == email


def create_user(db: Session, user_data: dict, verification_token: str) -> User | None:
    hashed_password = hash_password(user_data["password"])
    db_user = User(
        username=user_data["username"].strip(),
        email=user_data["email"].strip().lower(),
        password=hashed_password,
        is_verified=False,
        verification_token=verification_token,
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        logger.error(f"Error creating user {user_data.get('username')}: {e}")
        db.rollback()
        return None


def verify_user_email(db: Session, token: str) -> User | None:
    user = db.query(User).filter(User.verification_token == token).first()
    if user:
        try:
            user.is_verified = True
            user.verification_token = None
            db.commit()
            db.refresh(user)
            return user
        except Exception as e:
            logger.error(f"Error verifying email for user {user.id} with token {token}: {e}")
            db.rollback()
            return None
    return None


def set_password_reset_token(db: Session, user: User, token: str) -> bool:
    try:
        user.reset_token = token
        user.reset_token_expiry = datetime.now(UTC) + timedelta(
            minutes=settings.password_reset_token_expire_minutes
        )
        db.commit()
        return True
    except Exception as e:
        logger.error(f"Error saving reset token for user {user.id}: {e}")
        db.rollback()
        return False


def get_user_by_email_and_reset_token(db: Session, email: str, token: str) -> User | None:
    return (
        db.query(User)
        .filter(
            User.email == email,
            User.reset_token == token,
            User.reset_token_expiry > datetime.now(UTC),
        )
        .first()
    )


def reset_user_password(db: Session, user: User, new_password: str) -> bool:
    try:
        user.password = hash_password(new_password)
        user.reset_token = None
        user.reset_token_expiry = None
        db.commit()
        return True
    except Exception as e:
        logger.error(f"Error resetting password for user {user.id}: {e}")
        db.rollback()
        return False


def add_book(db: Session, book: Book):
    db.add(book)
    db.commit()


def delete_book(db: Session, book: Book):
    db.delete(book)
    db.commit()


def logout_current(db: Session, token: str):
    db.query(UserSession).filter(UserSession.token == token).delete()
    db.commit()


def logout_all(db: Session, user_id: int):
    db.query(UserSession).filter(UserSession.user_id == user_id).delete()
    db.commit()
