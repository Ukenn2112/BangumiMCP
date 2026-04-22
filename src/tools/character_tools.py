"""Character-related tools."""
from typing import Optional

from enums import CharacterType, SubjectType, PersonType, BloodType
from utils.api_client import make_bangumi_request, handle_api_error_response
from utils.formatters import format_character_summary
from utils.request_auth import has_effective_bangumi_token


def register(mcp):
    """Register all character tools with the MCP server."""

    @mcp.tool()
    async def search_characters(
        keyword: str, limit: int = 30, offset: int = 0, nsfw_filter: Optional[bool] = None
    ) -> str:
        """
        Search for characters on Bangumi.

        Supported Character Types (integer enum in result):
        1: Character, 2: Mechanic, 3: Ship, 4: Organization

        Args:
            keyword: The search keyword.
            limit: Pagination limit. Defaults to 30.
            offset: Pagination offset. Defaults to 0.
            nsfw_filter: Optional NSFW filter (boolean). Set to True to include, False to exclude. Requires authorization for non-default behavior.

        Returns:
            Formatted search results or an error message.
        """
        json_body = {"keyword": keyword, "filter": {}}
        if nsfw_filter is not None:
            json_body["filter"]["nsfw"] = nsfw_filter  # Filter is in JSON body

        params = {"limit": limit, "offset": offset}

        response = await make_bangumi_request(
            method="POST",
            path="/v0/search/characters",
            query_params=params,
            json_body=json_body,
        )

        error_msg = handle_api_error_response(response)
        if error_msg:
            return error_msg

        # Expecting a dictionary with 'data' and 'total'
        if not isinstance(response, dict) or "data" not in response:
            return f"Unexpected API response format for search_characters: {response}"

        characters = response.get("data", [])
        if not characters:
            return f"No characters found for keyword '{keyword}'."

        formatted_results = [format_character_summary(c) for c in characters]
        total = response.get("total", 0)
        results_text = (
            f"Found {len(characters)} characters (Total matched: {total}).\n"
            + "---\n".join(formatted_results)
        )

        return results_text

    @mcp.tool()
    async def get_character_details(character_id: int) -> str:
        """
        Get details of a specific character.

        Args:
            character_id: The ID of the character.

        Returns:
            Formatted character details or an error message.
        """
        response = await make_bangumi_request(
            method="GET", path=f"/v0/characters/{character_id}"
        )

        error_msg = handle_api_error_response(response)
        if error_msg:
            return error_msg

        # Expecting a dictionary
        if not isinstance(response, dict):
            return f"Unexpected API response format for get_character_details: {response}"

        character = response
        infobox = character.get("infobox")

        details_text = f"Character Details (ID: {character_id}):\n"
        details_text += f"  Name: {character.get('name')}\n"
        char_type_int = character.get("type")
        char_type_str = "Unknown Type"
        if char_type_int is not None:
            try:
                char_type_str = CharacterType(char_type_int).name
            except ValueError:
                char_type_str = f"Unknown Type ({char_type_int})"

        details_text += f"  Type: {char_type_str}\n"
        details_text += f"  Summary:\n{character.get('summary')}\n"
        details_text += f"  Locked: {character.get('locked')}\n"

        if character.get("gender"):
            details_text += f"  Gender: {character.get('gender')}\n"
        if character.get("blood_type") is not None:
            try:
                details_text += (
                    f"  Blood Type: {BloodType(character.get('blood_type')).name}\n"
                )
            except ValueError:
                details_text += f"  Blood Type: Unknown ({character.get('blood_type')})\n"

        if character.get("birth_year"):
            details_text += f"  Birth Date: {character.get('birth_year')}-{character.get('birth_mon')}-{character.get('birth_day')}\n"

        if infobox:
            details_text += (
                "  Infobox: (Details available in raw response, potentially complex)\n"
            )

        stat = character.get("stat", {})
        details_text += f"  Comments: {stat.get('comments', 0)}, Collections: {stat.get('collects', 0)}\n"

        images = character.get("images")
        if images and images.get("large"):
            details_text += f"  Image: {images.get('large')}\n"

        return details_text

    @mcp.tool()
    async def get_character_image(
        character_id: int, image_type: str = "large"
    ) -> str:
        """
        Get the image URL for a character.

        Supported image types:
        small, grid, large, medium

        Args:
            character_id: The ID of the character.
            image_type: The type of image to get. Defaults to 'large'.

        Returns:
            The image URL or an error message.
        """
        if image_type not in ["small", "grid", "large", "medium"]:
            return f"Invalid image_type: {image_type}. Must be one of: small, grid, large, medium"

        response = await make_bangumi_request(
            method="GET",
            path=f"/v0/characters/{character_id}/image",
            query_params={"type": image_type},
        )

        error_msg = handle_api_error_response(response)
        if error_msg:
            return error_msg

        if isinstance(response, dict) and "Location" in response:
            return f"Character Image URL: {response['Location']}"

        return f"Could not retrieve image for character ID {character_id}"

    @mcp.tool()
    async def get_character_subjects(character_id: int) -> str:
        """
        List subjects (e.g., anime, games) where a character appears.

        Args:
            character_id: The ID of the character.

        Returns:
            Formatted list of related subjects or an error message.
        """
        response = await make_bangumi_request(
            method="GET", path=f"/v0/characters/{character_id}/subjects"
        )

        error_msg = handle_api_error_response(response)
        if error_msg:
            return error_msg

        # Expecting a list of subjects
        if not isinstance(response, list):
            return f"Unexpected API response format for get_character_subjects: {response}"

        related_subjects = response
        if not related_subjects:
            return f"No subjects found related to character ID {character_id}."

        formatted_results = []
        for rel_subject in related_subjects:
            name = rel_subject.get("name")
            name_cn = rel_subject.get("name_cn")
            rel_id = rel_subject.get("id")
            rel_type_int = rel_subject.get("type")
            try:
                rel_type_str = (
                    SubjectType(rel_type_int).name
                    if rel_type_int is not None
                    else "Unknown Type"
                )
            except ValueError:
                rel_type_str = f"Unknown Type ({rel_type_int})"

            staff_info = rel_subject.get(
                "staff"
            )  # Staff refers to the role of the char in the subject e.g. "主角"

            formatted_results.append(
                f"Subject ID: {rel_id}, Name: {name_cn or name}, Type: {rel_type_str}, Role/Staff (in subject): {staff_info}"
            )

        return "Subjects This Character Appears In:\n" + "\n---\n".join(formatted_results)

    @mcp.tool()
    async def get_character_persons(character_id: int) -> str:
        """
        List persons (e.g., voice actors) related to a character.

        Args:
            character_id: The ID of the character.

        Returns:
            Formatted list of related persons or an error message.
        """
        response = await make_bangumi_request(
            method="GET", path=f"/v0/characters/{character_id}/persons"
        )

        error_msg = handle_api_error_response(response)
        if error_msg:
            return error_msg

        # Expecting a list of persons
        if not isinstance(response, list):
            return f"Unexpected API response format for get_character_persons: {response}"

        persons = response
        if not persons:
            return f"No persons found related to character ID {character_id}."

        formatted_results = []
        for person in persons:
            name = person.get("name")
            person_id = person.get("id")
            person_type_int = person.get("type")
            try:
                person_type_str = (
                    PersonType(person_type_int).name
                    if person_type_int is not None
                    else "Unknown Type"
                )
            except ValueError:
                person_type_str = f"Unknown Type ({person_type_int})"

            staff_info = person.get("staff")  # Role of the person for this character (e.g.,

            formatted_results.append(
                f"Person ID: {person_id}, Name: {name}, Type: {person_type_str}, Role (for character): {staff_info}"
            )

        return "Persons Related to This Character:\n" + "\n---\n".join(formatted_results)

    @mcp.tool()
    async def collect_character(character_id: int) -> str:
        """
        Collect (favorite) a character for the current user.

        Requires authentication (BANGUMI_TOKEN).

        Args:
            character_id: The ID of the character to collect.

        Returns:
            Success message or error.
        """
        if not has_effective_bangumi_token():
            return "BANGUMI_TOKEN is required for this operation."

        response = await make_bangumi_request(
            method="POST", path=f"/v0/characters/{character_id}/collect"
        )

        error_msg = handle_api_error_response(response)
        if error_msg:
            return error_msg

        # 204 No Content means success
        return f"Successfully collected character ID {character_id}."

    @mcp.tool()
    async def uncollect_character(character_id: int) -> str:
        """
        Remove a character from the current user's collection.

        Requires authentication (BANGUMI_TOKEN).

        Args:
            character_id: The ID of the character to uncollect.

        Returns:
            Success message or error.
        """
        if not has_effective_bangumi_token():
            return "BANGUMI_TOKEN is required for this operation."

        response = await make_bangumi_request(
            method="DELETE", path=f"/v0/characters/{character_id}/collect"
        )

        error_msg = handle_api_error_response(response)
        if error_msg:
            return error_msg

        return f"Successfully uncollected character ID {character_id}."
