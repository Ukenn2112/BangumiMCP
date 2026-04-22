"""Collection management tools."""
from typing import Any, Dict, List, Optional

from enums import SubjectType, CollectionType, EpisodeCollectionType, EpType
from utils.api_client import make_bangumi_request, handle_api_error_response
from utils.request_auth import has_effective_bangumi_token


def _format_episode_collection_status(status_value: Optional[int]) -> str:
    """
    Format episode collection status value to human-readable string.
    
    Args:
        status_value: EpisodeCollectionType enum value (1=Wish, 2=Done, 3=Dropped), or None
    
    Returns:
        Human-readable status string
    """
    if status_value == 1:
        return "Wish"
    elif status_value == 2:
        return "Done"
    elif status_value == 3:
        return "Dropped"
    else:
        return f"Unknown (status={status_value})"


def register(mcp):
    """Register all collection-related tools with the MCP server."""

    @mcp.tool()
    async def get_user_collections(
        username: str,
        subject_type: Optional[SubjectType] = None,
        collection_type: Optional[CollectionType] = None,
        limit: int = 30,
        offset: int = 0,
    ) -> str:
        """
        Get the collection list for a user.

        Collection types:
        1: Wish, 2: Collect, 3: Doing, 4: On Hold, 5: Dropped

        Args:
            username: The username.
            subject_type: Optional filter by subject type.
            collection_type: Optional filter by collection status (1-5).
            limit: Pagination limit. Defaults to 30.
            offset: Pagination offset. Defaults to 0.

        Returns:
            Formatted collection list or error.
        """
        query_params: Dict[str, Any] = {"limit": min(limit, 50), "offset": offset}
        if subject_type is not None:
            query_params["subject_type"] = int(subject_type)
        if collection_type is not None:
            query_params["type"] = int(collection_type)

        response = await make_bangumi_request(
            method="GET",
            path=f"/v0/users/{username}/collections",
            query_params=query_params,
        )

        error_msg = handle_api_error_response(response)
        if error_msg:
            return error_msg

        if not isinstance(response, dict) or "data" not in response:
            return f"Unexpected API response format: {response}"

        collections = response.get("data", [])
        if not collections:
            return f"No collections found for user {username}."

        status_map = {1: "Wish", 2: "Collected", 3: "Doing", 4: "On Hold", 5: "Dropped"}
        lines = [f"Collections for user {username}:"]
        lines.append(f"Total: {response.get('total', 0)}\n")

        for item in collections:
            subj = item.get("subject", {})
            name = subj.get("name_cn") or subj.get("name")
            subj_type = subj.get("type")
            status = status_map.get(item.get("type"), "Unknown")

            try:
                type_str = SubjectType(subj_type).name if subj_type else "?"
            except ValueError:
                type_str = f"?"

            lines.append(f"  [{type_str}] {name} - {status}")

        return "\n".join(lines)

    @mcp.tool()
    async def get_user_subject_collection(username: str, subject_id: int) -> str:
        """
        Get a user's collection status for a specific subject.

        Args:
            username: The username.
            subject_id: The subject ID.

        Returns:
            Collection details or error.
        """
        response = await make_bangumi_request(
            method="GET", path=f"/v0/users/{username}/collections/{subject_id}"
        )

        error_msg = handle_api_error_response(response)
        if error_msg:
            return error_msg

        if not isinstance(response, dict):
            return f"Unexpected API response format: {response}"

        coll = response
        details = f"Collection for {username} on subject {subject_id}:\n"
        details += f"  Type: {coll.get('type')}\n"
        if coll.get('ep_status') is not None:
            details += f"  Episode Status: {coll.get('ep_status')}\n"
        if coll.get('vol_status') is not None:
            details += f"  Volume Status: {coll.get('vol_status')}\n"
        if coll.get('rate'):
            details += f"  Rating: {coll.get('rate')}\n"
        if coll.get('comment'):
            details += f"  Comment: {coll.get('comment')}\n"

        return details

    @mcp.tool()
    async def update_subject_collection(
        subject_id: int,
        collection_type: Optional[CollectionType] = None,
        ep_status: Optional[int] = None,
        vol_status: Optional[int] = None,
        rating: Optional[int] = None,
        comment: Optional[str] = None,
    ) -> str:
        """
        Update the collection status for a subject.

        Collection types:
        1: Wish, 2: Collect, 3: Doing, 4: On Hold, 5: Dropped

        Args:
            subject_id: The subject ID.
            collection_type: Collection status (1-5).
            ep_status: Episode status (0-n).
            vol_status: Volume status (0-n).
            rating: Rating (0-10).
            comment: Personal comment.

        Returns:
            Success message or error.
        """
        if not has_effective_bangumi_token():
            return "BANGUMI_TOKEN is required for this operation."

        json_body: Dict[str, Any] = {}
        if collection_type is not None:
            json_body["type"] = int(collection_type)
        if ep_status is not None:
            json_body["ep_status"] = ep_status
        if vol_status is not None:
            json_body["vol_status"] = vol_status
        if rating is not None:
            json_body["rate"] = rating
        if comment is not None:
            json_body["comment"] = comment

        if not json_body:
            return "No updates were provided; specify at least one field to update."

        response = await make_bangumi_request(
            method="POST",
            path=f"/v0/users/-/collections/{subject_id}",
            json_body=json_body,
        )

        error_msg = handle_api_error_response(response)
        if error_msg:
            return error_msg

        return f"Successfully updated collection for subject {subject_id}."

    @mcp.tool()
    async def get_user_episode_collection(
        subject_id: int,
        episode_type: Optional[EpType] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> str:
        """
        Get the episode collection status for a subject.

        Args:
            subject_id: The subject ID.
            episode_type: Optional filter by episode type.
            limit: Pagination limit. Defaults to 100.
            offset: Pagination offset. Defaults to 0.

        Returns:
            Episode collection details or error.
        """
        if not has_effective_bangumi_token():
            return "BANGUMI_TOKEN is required for this operation."

        query_params: Dict[str, Any] = {"limit": min(limit, 1000), "offset": offset}
        if episode_type is not None:
            query_params["episode_type"] = int(episode_type)

        response = await make_bangumi_request(
            method="GET",
            path=f"/v0/users/-/collections/{subject_id}/episodes",
            query_params=query_params,
        )

        error_msg = handle_api_error_response(response)
        if error_msg:
            return error_msg

        if not isinstance(response, dict) or "data" not in response:
            return f"Unexpected API response format: {response}"

        episodes = response.get("data", [])
        if not episodes:
            return f"No episode collection found for subject {subject_id}."

        lines = [f"Episode collection for subject {subject_id}:"]
        for ep in episodes:
            # Each item is a UserEpisodeCollection; episode metadata is under "episode"
            episode_data = ep.get("episode") or {}

            ep_id = episode_data.get("id")
            ep_type = episode_data.get("type")
            # Top-level "type" represents collection status (e.g., watched / not watched)
            status = ep.get("type")
            name = (
                episode_data.get("name")
                or episode_data.get("name_cn")
                or ep.get("name")
                or ep.get("name_cn")
                or f"Episode {ep_id if ep_id is not None else '?'}"
            )

            try:
                type_str = EpType(ep_type).name if ep_type is not None else "?"
            except ValueError:
                type_str = "?"

            status_str = _format_episode_collection_status(status)
            lines.append(f"  [{type_str}] {name} - {status_str}")

        return "\n".join(lines)

    @mcp.tool()
    async def update_episode_collection(
        subject_id: int,
        episode_ids: List[int],
        collection_type: EpisodeCollectionType = EpisodeCollectionType.DONE,
    ) -> str:
        """
        Update the collection status for episodes.

        Episode collection types:
        1: Wish (想看), 2: Done (看过), 3: Dropped (抛弃)

        Args:
            subject_id: The subject ID.
            episode_ids: List of episode IDs to update.
            collection_type: Collection status (1=Wish, 2=Done, 3=Dropped). Defaults to 2 (Done/Watched).

        Returns:
            Success message or error.
        """
        if not has_effective_bangumi_token():
            return "BANGUMI_TOKEN is required for this operation."

        if not episode_ids:
            return "episode_ids cannot be empty; provide at least one episode ID."

        json_body = {
            "episode_id": episode_ids,
            "type": int(collection_type),
        }

        response = await make_bangumi_request(
            method="PATCH",
            path=f"/v0/users/-/collections/{subject_id}/episodes",
            json_body=json_body,
        )

        error_msg = handle_api_error_response(response)
        if error_msg:
            return error_msg

        return f"Successfully updated collection for {len(episode_ids)} episodes."

    @mcp.tool()
    async def get_single_episode_collection(episode_id: int) -> str:
        """
        Get the collection status for a single episode.

        Args:
            episode_id: The episode ID.

        Returns:
            Episode collection status or error.
        """
        if not has_effective_bangumi_token():
            return "BANGUMI_TOKEN is required for this operation."

        response = await make_bangumi_request(
            method="GET", path=f"/v0/users/-/collections/-/episodes/{episode_id}"
        )

        error_msg = handle_api_error_response(response)
        if error_msg:
            return error_msg

        if not isinstance(response, dict):
            return f"Unexpected API response format: {response}"

        ep = response
        ep_collection_type = ep.get("type")
        status = _format_episode_collection_status(ep_collection_type)
        details = f"Episode {episode_id} collection:\n"
        details += f"  Status: {status}\n"

        return details

    @mcp.tool()
    async def update_single_episode_collection(
        episode_id: int, collection_type: EpisodeCollectionType = EpisodeCollectionType.DONE
    ) -> str:
        """
        Update the collection status for a single episode.

        Args:
            episode_id: The episode ID.
            collection_type: Collection status (1=Wish, 2=Done, 3=Dropped). Defaults to 2 (Done/Watched).

        Returns:
            Success message or error.
        """
        if not has_effective_bangumi_token():
            return "BANGUMI_TOKEN is required for this operation."

        json_body = {"type": int(collection_type)}

        response = await make_bangumi_request(
            method="PUT",
            path=f"/v0/users/-/collections/-/episodes/{episode_id}",
            json_body=json_body,
        )

        error_msg = handle_api_error_response(response)
        if error_msg:
            return error_msg

        return f"Successfully updated collection for episode {episode_id}."

    @mcp.tool()
    async def get_user_character_collections(username: str) -> str:
        """
        Get a user's character collection list.

        Args:
            username: The username.

        Returns:
            Character collection list or error.
        """
        response = await make_bangumi_request(
            method="GET", path=f"/v0/users/{username}/collections/-/characters"
        )

        error_msg = handle_api_error_response(response)
        if error_msg:
            return error_msg

        if not isinstance(response, dict) or "data" not in response:
            return f"Unexpected API response format: {response}"

        characters = response.get("data", [])
        if not characters:
            return f"No character collections found for user {username}."

        lines = [f"Character collections for {username}:"]
        for char in characters:
            char_id = char.get("id")
            name = char.get("name")
            lines.append(f"  [ID: {char_id}] {name}")

        return "\n".join(lines)

    @mcp.tool()
    async def get_user_character_collection(
        username: str, character_id: int
    ) -> str:
        """
        Get a user's collection status for a specific character.

        Args:
            username: The username.
            character_id: The character ID.

        Returns:
            Character collection details or error.
        """
        response = await make_bangumi_request(
            method="GET",
            path=f"/v0/users/{username}/collections/-/characters/{character_id}",
        )

        error_msg = handle_api_error_response(response)
        if error_msg:
            return error_msg

        if not isinstance(response, dict):
            return f"Unexpected API response format: {response}"

        char = response
        details = f"Character collection for {username} on character {character_id}:\n"
        details += f"  ID: {char.get('id')}\n"
        details += f"  Name: {char.get('name')}\n"
        details += f"  Type: {char.get('type') or 'N/A'}\n"
        details += f"  Created at: {char.get('created_at') or 'N/A'}\n"

        images = char.get("images") or {}
        image_info = None
        if isinstance(images, dict):
            image_info = images.get("large") or images.get("medium") or images.get("small")
        details += f"  Image: {image_info or 'N/A'}\n"

        return details

    @mcp.tool()
    async def get_user_person_collections(username: str) -> str:
        """
        Get a user's person collection list.

        Args:
            username: The username.

        Returns:
            Person collection list or error.
        """
        response = await make_bangumi_request(
            method="GET", path=f"/v0/users/{username}/collections/-/persons"
        )

        error_msg = handle_api_error_response(response)
        if error_msg:
            return error_msg

        if not isinstance(response, dict) or "data" not in response:
            return f"Unexpected API response format: {response}"

        persons = response.get("data", [])
        if not persons:
            return f"No person collections found for user {username}."

        lines = [f"Person collections for {username}:"]
        for person in persons:
            person_id = person.get("id")
            name = person.get("name")
            lines.append(f"  [ID: {person_id}] {name}")

        return "\n".join(lines)

    @mcp.tool()
    async def get_user_person_collection(username: str, person_id: int) -> str:
        """
        Get a user's collection status for a specific person.

        Args:
            username: The username.
            person_id: The person ID.

        Returns:
            Person collection details or error.
        """
        response = await make_bangumi_request(
            method="GET",
            path=f"/v0/users/{username}/collections/-/persons/{person_id}",
        )

        error_msg = handle_api_error_response(response)
        if error_msg:
            return error_msg

        if not isinstance(response, dict):
            return f"Unexpected API response format: {response}"

        person = response
        details = f"Person collection for {username} on person {person_id}:\n"
        details += f"  ID: {person.get('id')}\n"
        details += f"  Name: {person.get('name')}\n"

        collection_type = person.get("type") or "N/A"
        career = person.get("career")
        if isinstance(career, list):
            career_str = ", ".join(str(c) for c in career)
        else:
            career_str = career or "N/A"
        created_at = person.get("created_at") or "N/A"

        details += f"  Type: {collection_type}\n"
        details += f"  Career: {career_str}\n"
        details += f"  Created at: {created_at}\n"

        return details
