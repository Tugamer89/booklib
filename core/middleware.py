from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from core.config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        csp = (
            "default-src 'self'; "
            "img-src 'self' data: https://res.cloudinary.com http://books.google.com https://books.google.com https://*.googleusercontent.com; "
            "connect-src 'self' https://www.googleapis.com https://cdn.tailwindcss.com https://unpkg.com; "
            "connect-src 'self' https://www.googleapis.com; "
            "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://unpkg.com; "
            "style-src 'self' 'unsafe-inline'; "
        )

        response.headers["Content-Security-Policy"] = csp
        return response


class PreventSessionOverwriteMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        if not request.session.get("remember_me"):
            return response

        new_raw_headers = []
        max_age_bytes = f"; Max-Age={settings.session_cookie_max_age_seconds}".encode()

        for key, value in response.raw_headers:
            if key == b"set-cookie" and value.startswith(b"session="):
                value += max_age_bytes
            new_raw_headers.append((key, value))

        response.raw_headers = new_raw_headers
        return response
