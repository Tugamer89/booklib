from fastapi import Request
from slowapi import Limiter, _rate_limit_exceeded_handler

from core.config import settings

__all__ = ["limiter", "_rate_limit_exceeded_handler"]


def get_client_ip(request: Request) -> str:
    """
    Securely extract the client IP address.
    If the application trusts all proxies (FORWARDED_ALLOW_IPS="*"), Uvicorn's ProxyHeadersMiddleware
    might extract a spoofed leftmost IP from X-Forwarded-For. In this case, we extract the IP
    from X-Real-IP, CF-Connecting-IP, or the rightmost IP of X-Forwarded-For.
    Otherwise, we rely on request.client.host which is handled securely by Uvicorn.
    """
    if settings.forwarded_allow_ips == "*" or settings.forwarded_allow_ips == ["*"]:
        headers = request.headers

        # Check cloudflare/nginx headers first
        if "X-Real-IP" in headers:
            return headers["X-Real-IP"].split(",")[0].strip()
        if "CF-Connecting-IP" in headers:
            return headers["CF-Connecting-IP"].split(",")[0].strip()

        # Fallback to the rightmost IP in X-Forwarded-For
        if "X-Forwarded-For" in headers:
            x_forwarded_for = headers["X-Forwarded-For"]
            ips = [ip.strip() for ip in x_forwarded_for.split(",")]
            if ips:
                return ips[-1]

    if not request.client or not request.client.host:
        return "127.0.0.1"

    return request.client.host


limiter = Limiter(key_func=get_client_ip)
