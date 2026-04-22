"""User-related tools."""

from utils.api_client import make_bangumi_request, handle_api_error_response
from utils.request_auth import has_effective_bangumi_token


def register(mcp):
    """Register user-related tools with the MCP server."""

    @mcp.tool()
    async def get_user_info(username: str) -> str:
        """
        Get user information by username.

        Args:
            username: The username to look up.

        Returns:
            Formatted user info or error.
        """
        response = await make_bangumi_request(
            method="GET", path=f"/v0/users/{username}"
        )

        error_msg = handle_api_error_response(response)
        if error_msg:
            return error_msg

        if not isinstance(response, dict):
            return f"Unexpected API response format: {response}"

        user = response
        details = f"User: {username}\n"
        details += f"  ID: {user.get('id')}\n"
        details += f"  Nickname: {user.get('nickname')}\n"
        if user.get('sign'):
            details += f"  Sign: {user.get('sign')}\n"

        return details

    @mcp.tool()
    async def get_user_avatar(username: str, avatar_type: str = "large") -> str:
        """
        Get the avatar URL for a user.

        Supported avatar types:
        small, large, medium

        Args:
            username: The username.
            avatar_type: The type of avatar. Defaults to 'large'.

        Returns:
            The avatar URL or error.
        """
        if avatar_type not in ["small", "large", "medium"]:
            return f"Invalid avatar_type: {avatar_type}. Must be one of: small, large, medium"

        response = await make_bangumi_request(
            method="GET",
            path=f"/v0/users/{username}/avatar",
            query_params={"type": avatar_type},
        )

        error_msg = handle_api_error_response(response)
        if error_msg:
            return error_msg

        if isinstance(response, dict) and "Location" in response:
            return f"User Avatar URL: {response['Location']}"

        return f"Could not retrieve avatar for user {username}"

    @mcp.tool()
    async def get_current_user() -> str:
        """
        Get the current user's information.

        Requires authentication (BANGUMI_TOKEN).

        Returns:
            Current user info or error.
        """
        if not has_effective_bangumi_token():
            return "BANGUMI_TOKEN is required for this operation."

        response = await make_bangumi_request(method="GET", path="/v0/me")

        error_msg = handle_api_error_response(response)
        if error_msg:
            return error_msg

        if not isinstance(response, dict):
            return f"Unexpected API response format: {response}"

        user = response
        details = f"Current User:\n"
        details += f"  ID: {user.get('id')}\n"
        details += f"  Username: {user.get('username')}\n"
        details += f"  Nickname: {user.get('nickname')}\n"
        if user.get('email'):
            details += f"  Email: {user.get('email')}\n"
        if user.get('reg_time'):
            details += f"  Registered: {user.get('reg_time')}\n"

        return details
