"""Person-related tools."""
from typing import List, Optional

from enums import PersonType, PersonCareer, BloodType, SubjectType, CharacterType
from utils.api_client import make_bangumi_request, handle_api_error_response
from utils.formatters import format_person_summary
from utils.request_auth import has_effective_bangumi_token


def register(mcp):
    """Register all person-related tools with the MCP server."""

    @mcp.tool()
    async def search_persons(
        keyword: str,
        limit: int = 30,
        offset: int = 0,
        career_filter: Optional[List[PersonCareer]] = None,
    ) -> str:
        """
        Search for persons or companies on Bangumi.

        Supported Person Types (integer enum in result):
        1: Individual, 2: Corporation, 3: Association

        Supported Career Filters (string enum):
        'producer', 'mangaka', 'artist', 'seiyu', 'writer', 'illustrator', 'actor'

        Args:
            keyword: The search keyword.
            limit: Pagination limit. Defaults to 30.
            offset: Pagination offset. Defaults to 0.
            career_filter: Optional filter by person career (list of strings from PersonCareer enum).

        Returns:
            Formatted search results or an error message.
        """
        json_body = {"keyword": keyword, "filter": {}}
        if career_filter:
            # Ensure string values for the API call using the enum values
            formatted_careers = [
                c.value if isinstance(c, PersonCareer) else str(c) for c in career_filter
            ]
            json_body["filter"]["career"] = formatted_careers  # Filter is in JSON body

        params = {"limit": limit, "offset": offset}  # Query parameters for the POST request

        response = await make_bangumi_request(
            method="POST",
            path="/v0/search/persons",
            query_params=params,
            json_body=json_body,
        )

        error_msg = handle_api_error_response(response)
        if error_msg:
            return error_msg

        # Expecting a dictionary with 'data' and 'total'
        if not isinstance(response, dict) or "data" not in response:
            return f"Unexpected API response format for search_persons: {response}"

        persons = response.get("data", [])
        if not persons:
            return f"No persons found for keyword '{keyword}'."

        formatted_results = [format_person_summary(p) for p in persons]
        total = response.get("total", 0)
        results_text = (
            f"Found {len(persons)} persons (Total matched: {total}).\n"
            + "---\n".join(formatted_results)
        )

        return results_text

    @mcp.tool()
    async def get_person_details(person_id: int) -> str:
        """
        Get details of a specific person or company.

        Args:
            person_id: The ID of the person/company.

        Returns:
            Formatted person details or an error message.
        """
        response = await make_bangumi_request(method="GET", path=f"/v0/persons/{person_id}")

        error_msg = handle_api_error_response(response)
        if error_msg:
            return error_msg

        # Expecting a dictionary
        if not isinstance(response, dict):
            return f"Unexpected API response format for get_person_details: {response}"

        person = response
        infobox = person.get("infobox")

        details_text = f"Person Details (ID: {person_id}):\n"
        details_text += f"  Name: {person.get('name')}\n"
        person_type_int = person.get("type")
        person_type_str = "Unknown Type"
        if person_type_int is not None:
            try:
                person_type_str = PersonType(person_type_int).name
            except ValueError:
                person_type_str = f"Unknown Type ({person_type_int})"

        details_text += f"  Type: {person_type_str}\n"
        details_text += f"  Summary:\n{person.get('summary')}\n"
        details_text += f"  Locked: {person.get('locked')}\n"
        details_text += f"  Careers: {', '.join(person.get('career') or [])}\n"

        if person.get("gender"):
            details_text += f"  Gender: {person.get('gender')}\n"
        if person.get("blood_type") is not None:
            try:
                details_text += (
                    f"  Blood Type: {BloodType(person.get('blood_type')).name}\n"
                )
            except ValueError:
                details_text += f"  Blood Type: Unknown ({person.get('blood_type')})\n"

        if person.get("birth_year"):
            details_text += f"  Birth Date: {person.get('birth_year')}-{person.get('birth_mon')}-{person.get('birth_day')}\n"

        if infobox:
            details_text += (
                "  Infobox: (Details available in raw response, potentially complex)\n"
            )

        stat = person.get("stat", {})
        details_text += f"  Comments: {stat.get('comments', 0)}, Collections: {stat.get('collects', 0)}\n"

        images = person.get("images")
        if images and images.get("large"):
            details_text += f"  Image: {images.get('large')}\n"

        return details_text

    @mcp.tool()
    async def get_person_subjects(person_id: int) -> str:
        """
        List subjects (e.g., anime, games) a person is related to (e.g., worked on).

        Args:
            person_id: The ID of the person.

        Returns:
            Formatted list of related subjects or an error message.
        """
        response = await make_bangumi_request(
            method="GET", path=f"/v0/persons/{person_id}/subjects"
        )

        error_msg = handle_api_error_response(response)
        if error_msg:
            return error_msg

        # Expecting a list of related subjects
        if not isinstance(response, list):
            return f"Unexpected API response format for get_person_subjects: {response}"

        related_subjects = response
        if not related_subjects:
            return f"No subjects found related to person ID {person_id}."

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
            )  # Role of the person in the subject e.g. "导演"

            formatted_results.append(
                f"Subject ID: {rel_id}, Name: {name_cn or name}, Type: {rel_type_str}, Role/Staff: {staff_info}"
            )

        return "Subjects This Person is Related To:\n" + "\n---\n".join(formatted_results)

    @mcp.tool()
    async def get_person_characters(person_id: int) -> str:
        """
        List characters voiced or portrayed by a person (e.g., voice actor, actor).

        Args:
            person_id: The ID of the person.

        Returns:
            Formatted list of related characters or an error message.
        """
        response = await make_bangumi_request(
            method="GET", path=f"/v0/persons/{person_id}/characters"
        )

        error_msg = handle_api_error_response(response)
        if error_msg:
            return error_msg

        # Expecting a list of characters
        if not isinstance(response, list):
            return f"Unexpected API response format for get_person_characters: {response}"

        characters = response
        if not characters:
            return f"No characters found related to person ID {person_id}."

        formatted_results = []
        for character in characters:
            name = character.get("name")
            char_id = character.get("id")
            char_type_int = character.get("type")
            try:
                char_type_str = (
                    CharacterType(char_type_int).name
                    if char_type_int is not None
                    else "Unknown Type"
                )
            except ValueError:
                char_type_str = f"Unknown Type ({char_type_int})"

            staff_info = character.get(
                "staff"
            )  # Role of the person for this character (e.g., Voice Actor name)

            formatted_results.append(
                f"Character ID: {char_id}, Name: {name}, Type: {char_type_str}, Role: {staff_info}"
            )

        return "Characters Related to This Person:\n" + "\n---\n".join(formatted_results)

    @mcp.tool()
    async def get_person_image(
        person_id: int, image_type: str = "large"
    ) -> str:
        """
        Get the image URL for a person.

        Supported image types:
        small, grid, large, medium

        Args:
            person_id: The ID of the person.
            image_type: The type of image to get. Defaults to 'large'.

        Returns:
            The image URL or an error message.
        """
        if image_type not in ["small", "grid", "large", "medium"]:
            return f"Invalid image_type: {image_type}. Must be one of: small, grid, large, medium"

        response = await make_bangumi_request(
            method="GET",
            path=f"/v0/persons/{person_id}/image",
            query_params={"type": image_type},
        )

        error_msg = handle_api_error_response(response)
        if error_msg:
            return error_msg

        if isinstance(response, dict) and "Location" in response:
            return f"Person Image URL: {response['Location']}"

        return f"Could not retrieve image for person ID {person_id}"

    @mcp.tool()
    async def collect_person(person_id: int) -> str:
        """
        Collect (favorite) a person for the current user.

        Requires authentication (BANGUMI_TOKEN).

        Args:
            person_id: The ID of the person to collect.

        Returns:
            Success message or error.
        """
        if not has_effective_bangumi_token():
            return "BANGUMI_TOKEN is required for this operation."

        response = await make_bangumi_request(
            method="POST", path=f"/v0/persons/{person_id}/collect"
        )

        error_msg = handle_api_error_response(response)
        if error_msg:
            return error_msg

        return f"Successfully collected person ID {person_id}."

    @mcp.tool()
    async def uncollect_person(person_id: int) -> str:
        """
        Remove a person from the current user's collection.

        Requires authentication (BANGUMI_TOKEN).

        Args:
            person_id: The ID of the person to uncollect.

        Returns:
            Success message or error.
        """
        if not has_effective_bangumi_token():
            return "BANGUMI_TOKEN is required for this operation."

        response = await make_bangumi_request(
            method="DELETE", path=f"/v0/persons/{person_id}/collect"
        )

        error_msg = handle_api_error_response(response)
        if error_msg:
            return error_msg

        return f"Successfully uncollected person ID {person_id}."
