"""Cloudflare Python Worker entrypoint for the public Bangumi MCP service."""

from __future__ import annotations

import asyncio
from functools import cache
from contextlib import asynccontextmanager
import sys
from pathlib import Path
from typing import Optional

SOURCE_DIR = Path(__file__).resolve().parent
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from server import get_mcp
from utils.request_auth import (
    extract_bearer_token,
    reset_request_bangumi_token,
    reset_request_bangumi_public_mode,
    set_request_bangumi_token,
    set_request_bangumi_public_mode,
)

try:
    from workers import WorkerEntrypoint
except ImportError:  # pragma: no cover - local import fallback
    class WorkerEntrypoint:  # type: ignore[override]
        """Fallback base class for local import-time validation."""

        def __init__(self, env=None):
            self.env = env


class AuthorizationContextMiddleware:
    """Bind the caller's Bearer token to the request context."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        public_mode_handle = set_request_bangumi_public_mode(True)
        header_token = _get_header(scope.get("headers", []), b"authorization")
        request_token = extract_bearer_token(header_token)
        if request_token is None:
            request_token = _get_header(scope.get("headers", []), b"authtoken")
            if request_token is not None:
                request_token = request_token.strip() or None
        token_handle = set_request_bangumi_token(request_token)

        try:
            await self.app(scope, receive, send)
        finally:
            reset_request_bangumi_token(token_handle)
            reset_request_bangumi_public_mode(public_mode_handle)


def _get_header(headers, key: bytes) -> Optional[str]:
    for header_key, header_value in headers:
        if header_key.lower() == key:
            return header_value.decode("latin-1")
    return None


@asynccontextmanager
async def _noop_lifespan(app):
    yield


@cache
def get_public_mcp_app():
    app = get_mcp().streamable_http_app()
    app.router.lifespan_context = _noop_lifespan
    app.add_middleware(AuthorizationContextMiddleware)
    return app


_public_mcp_start_lock = asyncio.Lock()
_public_mcp_started = False
_public_mcp_task_group = None


async def ensure_public_mcp_started():
    global _public_mcp_started, _public_mcp_task_group

    if _public_mcp_started:
        return

    async with _public_mcp_start_lock:
        if _public_mcp_started:
            return

        get_public_mcp_app()
        session_manager = get_mcp().session_manager

        if session_manager._task_group is None:
            await _start_task_group(session_manager)

        _public_mcp_started = True


async def _start_task_group(session_manager):
    task_group = await _enter_task_group()
    session_manager._task_group = task_group
    session_manager._has_started = True
    global _public_mcp_task_group
    _public_mcp_task_group = task_group


async def _enter_task_group():
    import anyio

    task_group = anyio.create_task_group()
    await task_group.__aenter__()
    return task_group


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        import asgi

        try:
            await ensure_public_mcp_started()
            return await asgi.fetch(get_public_mcp_app(), request.js_object, self.env)
        except Exception:
            import traceback

            traceback.print_exc()
            raise
