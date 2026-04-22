"""HTTP client utilities for Bangumi API."""
import asyncio
import json
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import httpx

from config import BANGUMI_API_BASE, USER_AGENT
from utils.request_auth import get_effective_bangumi_token

try:
    from pyodide.ffi import to_js as _to_js
    from js import Object as JSObject
    from js import fetch as worker_fetch
except ImportError:  # pragma: no cover - local stdio fallback
    _to_js = None
    JSObject = None
    worker_fetch = None


def _to_worker_js(value):
    if _to_js is None or JSObject is None:
        raise RuntimeError("Worker fetch bridge is unavailable.")
    return _to_js(value, dict_converter=JSObject.fromEntries)


def _build_request_url(path: str, query_params: Optional[Dict[str, Any]] = None) -> str:
    if not query_params:
        return f"{BANGUMI_API_BASE}{path}"

    return f"{BANGUMI_API_BASE}{path}?{urlencode(query_params, doseq=True)}"

# HTTP client timeout in seconds
HTTP_CLIENT_TIMEOUT = 30.0

# Shared httpx client for connection pooling
_client: Optional[httpx.AsyncClient] = None

# Initialize lock at module level, handling case where no event loop exists yet
try:
    _client_lock = asyncio.Lock()
except RuntimeError:
    # No event loop yet, will be created lazily on first use
    _client_lock = None


async def _ensure_lock():
    """Ensure the client lock is initialized."""
    global _client_lock
    if _client_lock is None:
        _client_lock = asyncio.Lock()


async def get_http_client() -> httpx.AsyncClient:
    """
    Get or create the shared HTTP client.

    Uses an asyncio.Lock for async-safe singleton pattern with connection pooling.
    The timeout applies to all requests made with this client.
    """
    global _client

    await _ensure_lock()

    async with _client_lock:
        if _client is None:
            _client = httpx.AsyncClient(
                follow_redirects=False,
                timeout=HTTP_CLIENT_TIMEOUT,
            )
    return _client


async def close_http_client():
    """
    Close the shared HTTP client and release resources.
    
    Should be called during application shutdown to properly clean up
    network connections and resources.
    """
    global _client
    
    await _ensure_lock()
    
    async with _client_lock:
        if _client is not None:
            await _client.aclose()
            _client = None


async def make_bangumi_request(
    method: str,
    path: str,
    query_params: Optional[Dict[str, Any]] = None,
    json_body: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
) -> Any:
    """Make a request to the Bangumi API with proper headers and error handling."""
    request_headers = headers.copy() if headers else {}
    request_headers["User-Agent"] = USER_AGENT
    request_headers["Accept"] = "application/json"

    # Prefer the request-scoped token, then fall back to the local env token.
    bangumi_token = get_effective_bangumi_token()
    if bangumi_token:
        request_headers["Authorization"] = f"Bearer {bangumi_token}"

    if worker_fetch is not None:
        return await _make_bangumi_request_with_fetch(
            method=method,
            path=path,
            query_params=query_params,
            json_body=json_body,
            request_headers=request_headers,
        )

    url = _build_request_url(path, query_params)

    client = await get_http_client()
    try:
        response = await client.request(
            method=method,
            url=url,
            params=query_params,
            json=json_body,
            headers=request_headers,
        )

        # Handle redirect responses (e.g., image endpoints) without attempting JSON parsing
        # Only handle redirect statuses that are expected to carry a Location header
        if response.status_code in (301, 302, 303, 307, 308):
            location = response.headers.get("Location")
            if location:
                return {"Location": location}
            return {
                "error": f"{response.status_code} redirect without Location",
                "status_code": response.status_code,
            }

        # Handle other 3xx codes that shouldn't have a Location header
        if 300 <= response.status_code < 400:
            return {
                "error": f"Unexpected redirect status: {response.status_code}",
                "status_code": response.status_code,
            }

        response.raise_for_status()

        # Some successful responses (e.g., 204 No Content) may have an empty body; avoid JSON parsing then
        if response.status_code == 204 or not response.content:
            return None

        # Return the raw JSON response, let the calling tool handle its structure (dict or list)
        return response.json()
    except httpx.HTTPStatusError as e:
        error_msg = (
            f"HTTP error occurred: {e.response.status_code} - {e.response.text}"
        )
        # Try to parse the error response body if it's JSON
        try:
            error_details = e.response.json()
            return {
                "error": error_msg,
                "status_code": e.response.status_code,
                "details": error_details,
            }
        except json.JSONDecodeError:
            return {
                "error": error_msg,
                "status_code": e.response.status_code,
                "details": e.response.text,
            }
    except httpx.RequestError as e:
        error_msg = (
            f"An error occurred while requesting {e.request.url!r}: "
            f"{type(e).__name__}: {e!r}"
        )
        return {"error": error_msg}
    except Exception as e:
        error_msg = f"An unexpected error occurred: {type(e).__name__}: {e!r}"
        return {"error": error_msg}


async def _make_bangumi_request_with_fetch(
    method: str,
    path: str,
    query_params: Optional[Dict[str, Any]],
    json_body: Optional[Dict[str, Any]],
    request_headers: Dict[str, str],
) -> Any:
    request_init: Dict[str, Any] = {
        "method": method,
        "headers": request_headers,
        "redirect": "manual",
    }
    if json_body is not None:
        request_headers["Content-Type"] = "application/json"
        request_init["body"] = json.dumps(json_body)

    response = await worker_fetch(
        _build_request_url(path, query_params),
        _to_worker_js(request_init),
    )

    status = response.status

    if status in (301, 302, 303, 307, 308):
        location = response.headers.get("Location")
        if location:
            return {"Location": location}
        return {
            "error": f"{status} redirect without Location",
            "status_code": status,
        }

    if 300 <= status < 400:
        return {
            "error": f"Unexpected redirect status: {status}",
            "status_code": status,
        }

    if status == 204:
        return None

    content_type = response.headers.get("Content-Type", "")
    response_text = await response.text()

    if status >= 400:
        details: Any = response_text
        if response_text:
            try:
                details = json.loads(response_text)
            except json.JSONDecodeError:
                details = response_text

        error_msg = f"HTTP error occurred: {status} - {response_text}"
        return {
            "error": error_msg,
            "status_code": status,
            "details": details,
        }

    if not response_text:
        return None

    if "json" in content_type.lower():
        return json.loads(response_text)

    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        return response_text


def handle_api_error_response(response: Any) -> Optional[str]:
    """
    Checks if the API response indicates an error and returns a formatted error message.
    Handles both dictionary-based errors and returns from make_bangumi_request on failure.
    """
    # Check for error structure returned by make_bangumi_request on HTTPStatusError or RequestError
    if isinstance(response, dict) and (
        "error" in response or "status_code" in response
    ):
        # This is an error dictionary created by our helper
        status_code = response.get("status_code", "N/A")
        error_msg = response.get("error", "Unknown error during request.")
        details = response.get("details", "")
        return f"Bangumi API Request Error (Status {status_code}): {error_msg}. Details: {details}".strip()

    # Check for error structure returned by Bangumi API itself (often dictionaries)
    # Safely check if the response is a dictionary before accessing its keys
    if isinstance(response, dict):
        if "title" in response and "description" in response:
            # This looks like a common Bangumi error response structure
            error_title = response.get("title", "API Error")
            error_description = response.get("description", "No description provided.")
            # The API might return a status code in the body too, or rely on HTTP status
            return f"Bangumi API Error: {error_title}. {error_description}".strip()

        # Check if it's a dictionary but *not* empty and *doesn't* look like a success response from list endpoints
        # Check for specific error fields if structure varies
        # Add more checks here if other error dictionary formats are observed
        # Example: if "message" in response and "code" in response: return f"API Error {response['code']}: {response['message']}"
        # Explicitly return None if dictionary doesn't match known error formats, indicating valid data response
        return None

    # If it's not a dictionary, or it's a dictionary that doesn't match known error formats, assume it's not an error
    return None
