"""Request-scoped Bangumi auth helpers."""

from contextvars import ContextVar, Token
from typing import Optional
import os

_request_bangumi_token: ContextVar[Optional[str]] = ContextVar(
    "request_bangumi_token", default=None
)
_request_bangumi_public_mode: ContextVar[bool] = ContextVar(
    "request_bangumi_public_mode", default=False
)


def extract_bearer_token(authorization_header: Optional[str]) -> Optional[str]:
    """Extract a bearer token from an Authorization header value."""
    if not authorization_header:
        return None

    scheme, _, credentials = authorization_header.partition(" ")
    if scheme.lower() != "bearer":
        return None

    token = credentials.strip()
    return token or None


def set_request_bangumi_token(token: Optional[str]) -> Token:
    """Bind a request-scoped Bangumi token for the current context."""
    return _request_bangumi_token.set(token)


def reset_request_bangumi_token(token: Token) -> None:
    """Restore the previous request-scoped Bangumi token."""
    _request_bangumi_token.reset(token)


def set_request_bangumi_public_mode(enabled: bool) -> Token:
    """Mark the current request as a public Worker request."""
    return _request_bangumi_public_mode.set(enabled)


def reset_request_bangumi_public_mode(token: Token) -> None:
    """Restore the previous public Worker request mode."""
    _request_bangumi_public_mode.reset(token)


def get_request_bangumi_token() -> Optional[str]:
    """Return the token bound to the current request context, if any."""
    return _request_bangumi_token.get()


def get_effective_bangumi_token() -> Optional[str]:
    """Return the request token first, then the process env fallback."""
    request_token = _request_bangumi_token.get()
    if request_token:
        return request_token

    if _request_bangumi_public_mode.get():
        return None

    env_token = os.getenv("BANGUMI_TOKEN")
    return env_token or None


def has_effective_bangumi_token() -> bool:
    """Return whether any Bangumi token is available for the current call."""
    return get_effective_bangumi_token() is not None
