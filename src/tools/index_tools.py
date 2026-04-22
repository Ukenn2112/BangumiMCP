"""Index management tools."""
from typing import Any, Dict, Optional

from enums import SubjectType
from utils.api_client import make_bangumi_request, handle_api_error_response
from utils.request_auth import has_effective_bangumi_token


def register(mcp):
    """Register all index management tools."""
    mcp.tool()(create_index)
    mcp.tool()(get_index)
    mcp.tool()(update_index)
    mcp.tool()(get_index_subjects)
    mcp.tool()(add_subject_to_index)
    mcp.tool()(update_index_subject)
    mcp.tool()(remove_subject_from_index)
    mcp.tool()(collect_index)
    mcp.tool()(uncollect_index)


async def create_index(title: str, description: str) -> str:
    """
    Create a new index (directory).

    Requires authentication (BANGUMI_TOKEN).

    Args:
        title: The title of the index.
        description: The description of the index.

    Returns:
        Index ID or error.
    """
    if not has_effective_bangumi_token():
        return "BANGUMI_TOKEN is required for this operation."

    json_body = {
        "title": title,
        "description": description,
    }

    response = await make_bangumi_request(
        method="POST", path="/v0/indices", json_body=json_body
    )

    error_msg = handle_api_error_response(response)
    if error_msg:
        return error_msg

    if not isinstance(response, dict):
        return f"Unexpected API response format: {response}"

    index_id = response.get("id")
    return f"Successfully created index. ID: {index_id}"


async def get_index(index_id: int) -> str:
    """
    Get index (directory) details.

    Args:
        index_id: The index ID.

    Returns:
        Index details or error.
    """
    response = await make_bangumi_request(
        method="GET", path=f"/v0/indices/{index_id}"
    )

    error_msg = handle_api_error_response(response)
    if error_msg:
        return error_msg

    if not isinstance(response, dict):
        return f"Unexpected API response format: {response}"

    idx = response
    details = f"Index {index_id}:\n"
    details += f"  Title: {idx.get('title')}\n"
    details += f"  Description: {idx.get('desc') or idx.get('description')}\n"
    details += f"  Creator: {idx.get('creator', {}).get('username') if isinstance(idx.get('creator'), dict) else idx.get('creator')}\n"
    details += f"  Created: {idx.get('created_at') or idx.get('created')}\n"
    details += f"  Subject Count: {idx.get('total', idx.get('subject_count', 0))}\n"

    return details


async def update_index(
    index_id: int, title: str, description: str
) -> str:
    """
    Update index (directory) information.

    Requires authentication (BANGUMI_TOKEN).

    Args:
        index_id: The index ID.
        title: New title.
        description: New description.

    Returns:
        Success message or error.
    """
    if not has_effective_bangumi_token():
        return "BANGUMI_TOKEN is required for this operation."

    json_body = {
        "title": title,
        "description": description,
    }

    response = await make_bangumi_request(
        method="PUT", path=f"/v0/indices/{index_id}", json_body=json_body
    )

    error_msg = handle_api_error_response(response)
    if error_msg:
        return error_msg

    return f"Successfully updated index {index_id}."


async def get_index_subjects(
    index_id: int,
    subject_type: Optional[SubjectType] = None,
    limit: int = 30,
    offset: int = 0,
) -> str:
    """
    Get subjects in an index.

    Args:
        index_id: The index ID.
        subject_type: Optional filter by subject type.
        limit: Pagination limit. Defaults to 30.
        offset: Pagination offset. Defaults to 0.

    Returns:
        Index subjects or error.
    """
    query_params: Dict[str, Any] = {
        "limit": min(limit, 50),
        "offset": offset,
    }
    if subject_type is not None:
        query_params["type"] = int(subject_type)

    response = await make_bangumi_request(
        method="GET", path=f"/v0/indices/{index_id}/subjects", query_params=query_params
    )

    error_msg = handle_api_error_response(response)
    if error_msg:
        return error_msg

    if not isinstance(response, dict) or "data" not in response:
        return f"Unexpected API response format: {response}"

    subjects = response.get("data", [])
    if not subjects:
        return f"No subjects found in index {index_id}."

    lines = [f"Subjects in index {index_id}:"]
    lines.append(f"Total: {response.get('total', 0)}\n")

    for subj in subjects:
        subj_id = subj.get("id")
        name = subj.get("title") or subj.get("name")
        lines.append(f"  [ID: {subj_id}] {name}")

    return "\n".join(lines)


async def add_subject_to_index(
    index_id: int, subject_id: int, comment: Optional[str] = None
) -> str:
    """
    Add a subject to an index.

    Requires authentication (BANGUMI_TOKEN).

    Args:
        index_id: The index ID.
        subject_id: The subject ID to add.
        comment: Optional comment.

    Returns:
        Success message or error.
    """
    if not has_effective_bangumi_token():
        return "BANGUMI_TOKEN is required for this operation."

    json_body: Dict[str, Any] = {"subject_id": subject_id}
    if comment is not None:
        json_body["comment"] = comment

    response = await make_bangumi_request(
        method="POST", path=f"/v0/indices/{index_id}/subjects", json_body=json_body
    )

    error_msg = handle_api_error_response(response)
    if error_msg:
        return error_msg

    return f"Successfully added subject {subject_id} to index {index_id}."


async def update_index_subject(
    index_id: int, subject_id: int, comment: Optional[str] = None
) -> str:
    """
    Update subject information in an index.

    Requires authentication (BANGUMI_TOKEN).

    Args:
        index_id: The index ID.
        subject_id: The subject ID to update.
        comment: New comment.

    Returns:
        Success message or error.
    """
    if not has_effective_bangumi_token():
        return "BANGUMI_TOKEN is required for this operation."

    json_body: Dict[str, Any] = {}
    if comment is not None:
        json_body["comment"] = comment

    if not json_body:
        return "No updates were provided; specify at least one field to update."

    response = await make_bangumi_request(
        method="PUT",
        path=f"/v0/indices/{index_id}/subjects/{subject_id}",
        json_body=json_body,
    )

    error_msg = handle_api_error_response(response)
    if error_msg:
        return error_msg

    return f"Successfully updated subject {subject_id} in index {index_id}."


async def remove_subject_from_index(
    index_id: int, subject_id: int
) -> str:
    """
    Remove a subject from an index.

    Requires authentication (BANGUMI_TOKEN).

    Args:
        index_id: The index ID.
        subject_id: The subject ID to remove.

    Returns:
        Success message or error.
    """
    if not has_effective_bangumi_token():
        return "BANGUMI_TOKEN is required for this operation."

    response = await make_bangumi_request(
        method="DELETE", path=f"/v0/indices/{index_id}/subjects/{subject_id}"
    )

    error_msg = handle_api_error_response(response)
    if error_msg:
        return error_msg

    return f"Successfully removed subject {subject_id} from index {index_id}."


async def collect_index(index_id: int) -> str:
    """
    Collect (favorite) an index for the current user.

    Requires authentication (BANGUMI_TOKEN).

    Args:
        index_id: The index ID.

    Returns:
        Success message or error.
    """
    if not has_effective_bangumi_token():
        return "BANGUMI_TOKEN is required for this operation."

    response = await make_bangumi_request(
        method="POST", path=f"/v0/indices/{index_id}/collect"
    )

    error_msg = handle_api_error_response(response)
    if error_msg:
        return error_msg

    return f"Successfully collected index {index_id}."


async def uncollect_index(index_id: int) -> str:
    """
    Remove an index from the current user's collection.

    Requires authentication (BANGUMI_TOKEN).

    Args:
        index_id: The index ID.

    Returns:
        Success message or error.
    """
    if not has_effective_bangumi_token():
        return "BANGUMI_TOKEN is required for this operation."

    response = await make_bangumi_request(
        method="DELETE", path=f"/v0/indices/{index_id}/collect"
    )

    error_msg = handle_api_error_response(response)
    if error_msg:
        return error_msg

    return f"Successfully uncollected index {index_id}."
