import re
from datetime import timedelta

from fastapi import HTTPException, status
from itsdangerous import BadSignature, URLSafeTimedSerializer

from core.config import settings

serializer = URLSafeTimedSerializer(settings.session_secret_key)


def validate_username(username: str):
    if not re.match(settings.username_regex, username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid username.")


def validate_password(password: str):
    if not re.match(settings.password_regex, password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Password too short or invalid."
        )


def validate_username_and_password(username: str, password: str):
    validate_username(username)
    validate_password(password)


def validate_email(email: str):
    if not re.match(settings.email_regex, email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email format.")


def generate_password_reset_token(email: str) -> str:
    return serializer.dumps(email, salt="password-reset-salt")


def verify_password_reset_token(token: str) -> str | None:
    try:
        email = serializer.loads(
            token,
            salt="password-reset-salt",
            max_age=timedelta(minutes=settings.password_reset_token_expire_minutes).total_seconds(),
        )
        return email
    except BadSignature:
        return None


def generate_verification_token(email: str) -> str:
    return serializer.dumps(email, salt="email-verification-salt")


def verify_verification_token(token: str) -> str | None:
    try:
        email = serializer.loads(
            token, salt="email-verification-salt", max_age=timedelta(days=7).total_seconds()
        )
        return email
    except BadSignature:
        return None


def hash_password(password: str) -> str:
    return settings.password_hash.hash(password)


def verify_password(secret: str, password: str) -> bool:
    return settings.password_hash.verify(secret, password)


def get_safe_redirect_url(url: str | None, request_host: str) -> str:
    """Sanitize the redirect URL to prevent Open Redirects and XSS."""
    if not url:
        return "/"

    url = url.strip()

    if (
        url.startswith("//")
        or url.startswith("\\\\")
        or url.startswith("/\\")
        or url.startswith("\\/")
    ):
        return "/"

    from urllib.parse import urlparse

    parsed = urlparse(url)

    if parsed.scheme and parsed.scheme not in ("http", "https"):
        return "/"

    if parsed.netloc and parsed.netloc != request_host:
        return "/"

    return url
