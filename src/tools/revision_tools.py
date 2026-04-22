"""Revision/history tools."""
import json
from typing import Any, Dict

from utils.api_client import make_bangumi_request, handle_api_error_response


def register(mcp):
    """Register all revision/history tools with the MCP server."""

    @mcp.tool()
    async def get_person_revisions(
        person_id: int,
        limit: int = 30,
        offset: int = 0,
    ) -> str:
        """
        Get revision history for a person.

        Args:
            person_id: The person ID.
            limit: Pagination limit. Defaults to 30.
            offset: Pagination offset. Defaults to 0.

        Returns:
            Revision history or error.
        """
        query_params: Dict[str, Any] = {
            "person_id": person_id,
            "limit": min(limit, 50),
            "offset": offset,
        }

        response = await make_bangumi_request(
            method="GET", path="/v0/revisions/persons", query_params=query_params
        )

        error_msg = handle_api_error_response(response)
        if error_msg:
            return error_msg

        if not isinstance(response, dict) or "data" not in response:
            return f"Unexpected API response format: {response}"

        revisions = response.get("data", [])
        if not revisions:
            return f"No revisions found for person ID {person_id}."

        lines = [f"Revisions for person {person_id}:"]
        lines.append(f"Total: {response.get('total', 0)}\n")

        for rev in revisions:
            rev_id = rev.get("id")
            summary = rev.get("summary") or "No summary"
            created_at = rev.get("created_at") or "Unknown"
            creator = rev.get("creator", {}) or {}
            username = creator.get("username") if creator else "Unknown"

            lines.append(f"  [ID: {rev_id}] {summary} by {username} at {created_at}")

        return "\n".join(lines)

    @mcp.tool()
    async def get_person_revision(revision_id: int) -> str:
        """
        Get details of a specific person revision.

        Args:
            revision_id: The revision ID.

        Returns:
            Revision details or error.
        """
        response = await make_bangumi_request(
            method="GET", path=f"/v0/revisions/persons/{revision_id}"
        )

        error_msg = handle_api_error_response(response)
        if error_msg:
            return error_msg

        if not isinstance(response, dict):
            return f"Unexpected API response format: {response}"

        rev = response
        details = f"Revision {revision_id} Details:\n"
        details += f"  Type: {rev.get('type')}\n"

        created_at = rev.get("created_at")
        if created_at is not None:
            details += f"  Created At: {created_at}\n"

        creator = rev.get("creator") or {}
        if isinstance(creator, dict) and creator:
            username = creator.get("username") or creator.get("name") or "Unknown"
            details += f"  Creator: {username}\n"

        summary = rev.get("summary")
        if summary:
            details += f"  Summary: {summary}\n"

        data = rev.get("data")
        if data is not None:
            if isinstance(data, dict):
                keys = ", ".join(sorted(map(str, data.keys()))) if data else "no fields"
                details += f"  Data fields: {keys}\n"
            else:
                details += f"  Data: {data}\n"

        return details

    @mcp.tool()
    async def get_character_revisions(
        character_id: int,
        limit: int = 30,
        offset: int = 0,
    ) -> str:
        """
        Get revision history for a character.

        Args:
            character_id: The character ID.
            limit: Pagination limit. Defaults to 30.
            offset: Pagination offset. Defaults to 0.

        Returns:
            Revision history or error.
        """
        query_params: Dict[str, Any] = {
            "character_id": character_id,
            "limit": min(limit, 50),
            "offset": offset,
        }

        response = await make_bangumi_request(
            method="GET", path="/v0/revisions/characters", query_params=query_params
        )

        error_msg = handle_api_error_response(response)
        if error_msg:
            return error_msg

        if not isinstance(response, dict) or "data" not in response:
            return f"Unexpected API response format: {response}"

        revisions = response.get("data", [])
        if not revisions:
            return f"No revisions found for character ID {character_id}."

        lines = [f"Revisions for character {character_id}:"]
        lines.append(f"Total: {response.get('total', 0)}\n")

        for rev in revisions:
            rev_id = rev.get("id")
            summary = rev.get("summary") or "No summary"
            created_at = rev.get("created_at") or "Unknown"
            creator = rev.get("creator", {}) or {}
            username = creator.get("username") if creator else "Unknown"

            lines.append(f"  [ID: {rev_id}] {summary} by {username} at {created_at}")

        return "\n".join(lines)

    @mcp.tool()
    async def get_character_revision(revision_id: int) -> str:
        """
        Get details of a specific character revision.

        Args:
            revision_id: The revision ID.

        Returns:
            Revision details or error.
        """
        response = await make_bangumi_request(
            method="GET", path=f"/v0/revisions/characters/{revision_id}"
        )

        error_msg = handle_api_error_response(response)
        if error_msg:
            return error_msg

        if not isinstance(response, dict):
            return f"Unexpected API response format: {response}"

        rev = response
        details = f"Revision {revision_id} Details:\n"
        details += f"  Type: {rev.get('type')}\n"

        created_at = rev.get("created_at")
        if created_at is not None:
            details += f"  Created At: {created_at}\n"

        creator = rev.get("creator", {}) or {}
        if creator:
            details += f"  Creator: {creator.get('username')}\n"

        if rev.get("summary"):
            details += f"  Summary: {rev.get('summary')}\n"

        data = rev.get("data")
        if data is not None:
            # Pretty-print data in case it is a structured object
            details += "  Data:\n"
            details += json.dumps(data, ensure_ascii=False, indent=2)
            details += "\n"

        return details

    @mcp.tool()
    async def get_subject_revisions(
        subject_id: int,
        limit: int = 30,
        offset: int = 0,
    ) -> str:
        """
        Get revision history for a subject.

        Args:
            subject_id: The subject ID.
            limit: Pagination limit. Defaults to 30.
            offset: Pagination offset. Defaults to 0.

        Returns:
            Revision history or error.
        """
        query_params: Dict[str, Any] = {
            "subject_id": subject_id,
            "limit": min(limit, 50),
            "offset": offset,
        }

        response = await make_bangumi_request(
            method="GET", path="/v0/revisions/subjects", query_params=query_params
        )

        error_msg = handle_api_error_response(response)
        if error_msg:
            return error_msg

        if not isinstance(response, dict) or "data" not in response:
            return f"Unexpected API response format: {response}"

        revisions = response.get("data", [])
        if not revisions:
            return f"No revisions found for subject ID {subject_id}."

        lines = [f"Revisions for subject {subject_id}:"]
        lines.append(f"Total: {response.get('total', 0)}\n")

        for rev in revisions:
            rev_id = rev.get("id")
            summary = rev.get("summary") or "No summary"
            created_at = rev.get("created_at") or "Unknown"
            creator = rev.get("creator", {}) or {}
            username = creator.get("username") if creator else "Unknown"

            lines.append(f"  [ID: {rev_id}] {summary} by {username} at {created_at}")

        return "\n".join(lines)

    @mcp.tool()
    async def get_subject_revision(revision_id: int) -> str:
        """
        Get details of a specific subject revision.

        Args:
            revision_id: The revision ID.

        Returns:
            Revision details or error.
        """
        response = await make_bangumi_request(
            method="GET", path=f"/v0/revisions/subjects/{revision_id}"
        )

        error_msg = handle_api_error_response(response)
        if error_msg:
            return error_msg

        if not isinstance(response, dict):
            return f"Unexpected API response format: {response}"

        rev = response
        details = f"Revision {revision_id} Details:\n"
        details += f"  Type: {rev.get('type')}\n"

        created_at = rev.get("created_at")
        if created_at is not None:
            details += f"  Created at: {created_at}\n"

        creator = rev.get("creator", {})
        if creator:
            # Try common identity fields; fall back to a generic representation
            name = creator.get("nickname") or creator.get("username") or creator.get("name")
            if name:
                details += f"  Creator: {name}\n"
            else:
                details += f"  Creator: {creator}\n"

        if rev.get("summary"):
            details += f"  Summary: {rev.get('summary')}\n"

        data = rev.get("data")
        if data is not None:
            # Pretty-print the data payload for readability
            formatted_data = json.dumps(data, ensure_ascii=False, indent=2)
            details += f"  Data:\n{formatted_data}\n"

        return details

    @mcp.tool()
    async def get_episode_revisions(
        episode_id: int,
        limit: int = 30,
        offset: int = 0,
    ) -> str:
        """
        Get revision history for an episode.

        Args:
            episode_id: The episode ID.
            limit: Pagination limit. Defaults to 30.
            offset: Pagination offset. Defaults to 0.

        Returns:
            Revision history or error.
        """
        query_params: Dict[str, Any] = {
            "episode_id": episode_id,
            "limit": min(limit, 50),
            "offset": offset,
        }

        response = await make_bangumi_request(
            method="GET", path="/v0/revisions/episodes", query_params=query_params
        )

        error_msg = handle_api_error_response(response)
        if error_msg:
            return error_msg

        if not isinstance(response, dict) or "data" not in response:
            return f"Unexpected API response format: {response}"

        revisions = response.get("data", [])
        if not revisions:
            return f"No revisions found for episode ID {episode_id}."

        lines = [f"Revisions for episode {episode_id}:"]
        lines.append(f"Total: {response.get('total', 0)}\n")

        for rev in revisions:
            rev_id = rev.get("id")
            summary = rev.get("summary") or "No summary"
            created_at = rev.get("created_at") or "Unknown"
            creator = rev.get("creator", {}) or {}
            username = creator.get("username") if creator else "Unknown"

            lines.append(f"  [ID: {rev_id}] {summary} by {username} at {created_at}")

        return "\n".join(lines)

    @mcp.tool()
    async def get_episode_revision(revision_id: int) -> str:
        """
        Get details of a specific episode revision.

        Args:
            revision_id: The revision ID.

        Returns:
            Revision details or error.
        """
        response = await make_bangumi_request(
            method="GET", path=f"/v0/revisions/episodes/{revision_id}"
        )

        error_msg = handle_api_error_response(response)
        if error_msg:
            return error_msg

        if not isinstance(response, dict):
            return f"Unexpected API response format: {response}"

        rev = response
        details = f"Revision {revision_id} Details:\n"
        details += f"  Type: {rev.get('type')}\n"

        creator = rev.get("creator")
        if isinstance(creator, dict):
            username = creator.get("username") or creator.get("name") or creator.get("id")
            if username is not None:
                details += f"  Creator: {username}\n"
        elif creator is not None:
            details += f"  Creator: {creator}\n"

        created_at = rev.get("created_at")
        if created_at is not None:
            details += f"  Created at: {created_at}\n"

        summary = rev.get("summary")
        if summary:
            details += f"  Summary: {summary}\n"

        data = rev.get("data")
        if data is not None:
            if isinstance(data, (dict, list)):
                pretty_data = json.dumps(data, ensure_ascii=False, indent=2)
                details += f"  Data:\n{pretty_data}\n"
            else:
                details += f"  Data: {data}\n"

        return details
