"""Subject and episode related tools."""
from typing import Any, Dict, Optional

from enums import SubjectType, EpType, PersonType, CharacterType
from utils.api_client import make_bangumi_request, handle_api_error_response
from utils.formatters import format_subject_summary


def register(mcp):
    """Register all subject-related tools with the MCP server."""

    @mcp.tool()
    async def get_daily_broadcast() -> str:
        """
        Get the daily broadcast schedule for the current week on Bangumi.

        Returns:
            The broadcast schedule grouped by day of the week, or an error message.
        """
        response = await make_bangumi_request(method="GET", path="/calendar")

        error_msg = handle_api_error_response(response)
        if error_msg:
            return error_msg

        # Expecting a list of dictionaries, where each dict represents a day
        if not isinstance(response, list):
            return f"Unexpected API response format for /calendar: {response}"

        calendar_data = response
        if not calendar_data:
            return "Could not retrieve daily broadcast calendar."

        formatted_schedule = ["Daily Broadcast Schedule:"]

        # The API returns days in a specific order, we can just iterate through the list
        for day_entry in calendar_data:
            weekday = day_entry.get("weekday", {})
            items = day_entry.get("items", [])

            # Get readable weekday name, default to English if others are missing
            weekday_name = (
                weekday.get("cn")
                or weekday.get("ja")
                or weekday.get("en")
                or f"Weekday ID {weekday.get('id', 'N/A')}"
            )
            formatted_schedule.append(f"\n--- {weekday_name} ---")

            if not items:
                formatted_schedule.append("  No broadcasts scheduled.")
            else:
                formatted_results = [format_subject_summary(s) for s in items]
                results_text = (
                    f"Found {len(items)} subjects.\n"
                    + "---\n".join(formatted_results)
                )
                formatted_schedule.append(results_text)

        return "\n".join(formatted_schedule)

    @mcp.tool()
    async def search_subjects(
        keyword: str,
        subject_type: Optional[SubjectType] = None,
        sort: str = "match",
        limit: int = 30,
        offset: int = 0,
    ) -> str:
        """
        Search for subjects on Bangumi.

        Supported Subject Types (integer enum):
        1: Book, 2: Anime, 3: Music, 4: Game, 6: Real

        Supported Sort orders (string enum):
        'match', 'heat', 'rank', 'score'

        Args:
            keyword: The search keyword.
            subject_type: Optional filter by subject type. Use integer values (1, 2, 3, 4, 6).
            sort: Optional sort order. Defaults to 'match'.
            limit: Pagination limit. Max 50. Defaults to 30.
            offset: Pagination offset. Defaults to 0.

        Returns:
            Formatted search results or an error message.
        """
        json_body = {"keyword": keyword, "sort": sort, "filter": {}}
        if subject_type is not None:
            json_body["filter"]["type"] = [int(subject_type)]

        params = {"limit": min(limit, 50), "offset": offset}  # Enforce max limit

        response = await make_bangumi_request(
            method="POST",
            path="/v0/search/subjects",
            query_params=params,  # Pass limit/offset as query params
            json_body=json_body,  # Pass keyword and filter as JSON body
        )

        error_msg = handle_api_error_response(response)
        if error_msg:
            return error_msg

        # Expecting a dictionary with 'data' and 'total'
        if not isinstance(response, dict) or "data" not in response:
            return f"Unexpected API response format for search_subjects: {response}"

        subjects = response.get("data", [])
        if not subjects:
            return f"No subjects found for keyword '{keyword}'."

        formatted_results = [format_subject_summary(s) for s in subjects]
        total = response.get("total", 0)
        results_text = (
            f"Found {len(subjects)} subjects (Total matched: {total}).\n"
            + "---\n".join(formatted_results)
        )

        return results_text

    @mcp.tool()
    async def browse_subjects(
        subject_type: SubjectType,
        cat: Optional[int] = None,
        series: Optional[bool] = None,
        platform: Optional[str] = None,
        sort: Optional[str] = None,
        year: Optional[int] = None,
        month: Optional[int] = None,
        limit: int = 30,
        offset: int = 0,
    ) -> str:
        """
        Browse subjects by type and filters.

        Supported Subject Types (integer enum, required):
        1: Book, 2: Anime, 3: Music, 4: Game, 6: Real

        Supported Categories (integer enums for 'cat', specific to SubjectType):
        Book (type=1): Other=0, Comic=1001, Novel=1002, Illustration=1003
        Anime (type=2): Other=0, TV=1, OVA=2, Movie=3, WEB=5
        Game (type=4): Other=0, Games=4001, Software=4002, DLC=4003, Tabletop=4005
        Real (type=6): Other=0, JP=1, EN=2, CN=3, TV=6001, Movie=6002, Live=6003, Show=6004

        Supported Sort orders (string for 'sort', optional):
        'date', 'rank' (Default sorting may vary if 'sort' is not provided)

        Args:
            subject_type: Required filter by subject type (integer value from SubjectType enum).
            cat: Optional filter by subject category (integer value from category enums).
            series: Optional filter for books (type=1). True for series main entry.
            platform: Optional filter for games (type=4). E.g. 'Web', 'PC', 'PS4'.
            sort: Optional sort order ('date' or 'rank').
            year: Optional filter by year.
            month: Optional filter by month (1-12).
            limit: Pagination limit. Max 50. Defaults to 30.
            offset: Pagination offset. Defaults to 0.

        Returns:
            Formatted list of subjects or an error message.
        """
        query_params: Dict[str, Any] = {
            "type": int(subject_type),
            "limit": min(limit, 50),
            "offset": offset,
        }
        if cat is not None:
            query_params["cat"] = cat
        if series is not None:
            query_params["series"] = series
        if platform is not None:
            query_params["platform"] = platform
        if sort is not None:
            query_params["sort"] = sort
        if year is not None:
            query_params["year"] = year
        if month is not None:
            query_params["month"] = month

        response = await make_bangumi_request(
            method="GET", path="/v0/subjects", query_params=query_params
        )

        error_msg = handle_api_error_response(response)
        if error_msg:
            return error_msg

        # Expecting a dictionary with 'data' and 'total'
        if not isinstance(response, dict) or "data" not in response:
            return f"Unexpected API response format for browse_subjects: {response}"

        subjects = response.get("data", [])
        if not subjects:
            return f"No subjects found for the given criteria."

        formatted_results = [format_subject_summary(s) for s in subjects]
        total = response.get("total", 0)
        results_text = f"Found {len(subjects)} subjects (Total: {total}).\n" + "---\n".join(
            formatted_results
        )

        return results_text

    @mcp.tool()
    async def get_subject_details(subject_id: int) -> str:
        """
        Get details of a specific subject (e.g., anime, book, game).

        Args:
            subject_id: The ID of the subject.

        Returns:
            Formatted subject details or an error message.
        """
        response = await make_bangumi_request(
            method="GET", path=f"/v0/subjects/{subject_id}"
        )

        error_msg = handle_api_error_response(response)
        if error_msg:
            return error_msg

        # Expecting a dictionary
        if not isinstance(response, dict):
            return f"Unexpected API response format for get_subject_details: {response}"

        subject = response
        infobox = subject.get("infobox")
        tags = subject.get("tags")

        details_text = f"Subject Details (ID: {subject_id}):\n"
        details_text += f"  Name: {subject.get('name')}\n"
        if subject.get("name_cn"):
            details_text += f"  Chinese Name: {subject.get('name_cn')}\n"
        try:
            details_text += f"  Type: {SubjectType(subject.get('type')).name if subject.get('type') is not None else 'Unknown Type'}\n"
        except ValueError:
            details_text += f"  Type: Unknown Type ({subject.get('type')})\n"

        if subject.get("date"):
            details_text += f"  Date: {subject.get('date')}\n"
        if subject.get("platform"):
            details_text += f"  Platform: {subject.get('platform')}\n"
        if subject.get("volumes"):
            details_text += f"  Volumes: {subject.get('volumes')}\n"
        if subject.get("eps") is not None:  # Could be 0
            details_text += f"  Episodes (Wiki): {subject.get('eps')}\n"
        if subject.get("total_episodes"):
            details_text += f"  Episodes (DB): {subject.get('total_episodes')}\n"

        details_text += f"  Summary:\n{subject.get('summary')}\n"

        if subject.get("rating", {}).get("score") is not None:
            details_text += f"  Score: {subject['rating'].get('score')} (Votes: {subject['rating'].get('total')})\n"
        if subject.get("rating", {}).get("rank") is not None:
            details_text += f"  Rank: {subject['rating'].get('rank')}\n"

        if tags:
            tags_list = [f"{t['name']} ({t['count']})" for t in tags]
            details_text += f"  Tags: {', '.join(tags_list)}\n"

        if infobox:
            details_text += (
                "  Infobox: (Details available in raw response, potentially complex)\n"
            )

        if "collection" in subject:  # requires auth and user had collected it
            collection = subject["collection"]
            details_text += f"  Collection (Total Users): Wish: {collection.get('wish',0)}, Collected: {collection.get('collect',0)}, Doing: {collection.get('doing',0)}, On Hold: {collection.get('on_hold',0)}, Dropped: {collection.get('dropped',0)}\n"

        images = subject.get("images")
        if images and images.get("large"):
            details_text += f"  Cover Image: {images.get('large')}\n"

        return details_text

    @mcp.tool()
    async def get_subject_image(
        subject_id: int, image_type: str = "large"
    ) -> str:
        """
        Get the image URL for a subject.

        Supported image types:
        small, grid, large, medium, common

        Args:
            subject_id: The ID of the subject.
            image_type: The type of image to get. Defaults to 'large'.

        Returns:
            The image URL or an error message.
        """
        if image_type not in ["small", "grid", "large", "medium", "common"]:
            return f"Invalid image_type: {image_type}. Must be one of: small, grid, large, medium, common"

        response = await make_bangumi_request(
            method="GET",
            path=f"/v0/subjects/{subject_id}/image",
            query_params={"type": image_type},
        )

        error_msg = handle_api_error_response(response)
        if error_msg:
            return error_msg

        if isinstance(response, dict) and "Location" in response:
            return f"Subject Image URL: {response['Location']}"

        return f"Could not retrieve image for subject ID {subject_id}"

    @mcp.tool()
    async def get_subject_persons(subject_id: int) -> str:
        """
        List persons (staff, cast) related to a subject.

        Args:
            subject_id: The ID of the subject.

        Returns:
            Formatted list of related persons or an error message.
        """
        response = await make_bangumi_request(
            method="GET", path=f"/v0/subjects/{subject_id}/persons"
        )

        error_msg = handle_api_error_response(response)
        if error_msg:
            return error_msg

        # Expecting a list of persons
        if not isinstance(response, list):
            return f"Unexpected API response format for get_subject_persons: {response}"

        persons = response
        if not persons:
            return f"No persons found related to subject ID {subject_id}."

        formatted_results = []
        for person in persons:
            name = person.get("name")
            person_id = person.get("id")
            relation = person.get("relation")  # e.g., "导演", "动画制作", "声优"
            career = ", ".join(
                person.get("career", []) or []
            )  # person.get('career') could be None or empty list
            eps = person.get("eps")  # Participation in episodes/tracks for THIS subject

            # Safely get person type name if available and is valid enum value
            person_type_int = person.get("type")
            person_type_str = "Unknown Type"
            if person_type_int is not None:
                try:
                    person_type_str = PersonType(person_type_int).name
                except ValueError:
                    person_type_str = f"Unknown Type ({person_type_int})"

            formatted_results.append(
                f"Person ID: {person_id}, Name: {name}, Type: {person_type_str}, Relation (in subject): {relation}, Overall Career: {career}, Participating Episodes/Tracks: {eps}"
            )

        return "Related Persons:\n" + "\n---\n".join(formatted_results)

    @mcp.tool()
    async def get_subject_characters(subject_id: int) -> str:
        """
        List characters related to a subject.

        Args:
            subject_id: The ID of the subject.

        Returns:
            Formatted list of related characters or an error message.
        """
        response = await make_bangumi_request(
            method="GET", path=f"/v0/subjects/{subject_id}/characters"
        )

        error_msg = handle_api_error_response(response)
        if error_msg:
            return error_msg

        # Expecting a list of characters
        if not isinstance(response, list):
            return f"Unexpected API response format for get_subject_characters: {response}"

        characters = response
        if not characters:
            return f"No characters found related to subject ID {subject_id}."

        formatted_results = []
        for character in characters:
            name = character.get("name")
            char_id = character.get("id")
            relation = character.get("relation")
            actors = ", ".join(
                [a.get("name") for a in character.get("actors", []) if a.get("name")] or []
            )

            # Safely get character type name
            char_type_int = character.get("type")
            char_type_str = "Unknown Type"
            if char_type_int is not None:
                try:
                    char_type_str = CharacterType(char_type_int).name
                except ValueError:
                    char_type_str = f"Unknown Type ({char_type_int})"

            formatted_results.append(
                f"Character ID: {char_id}, Name: {name}, Type: {char_type_str}, Relation (in subject): {relation}, Voice Actors: {actors}"
            )

        return "Related Characters:\n" + "\n---\n".join(formatted_results)

    @mcp.tool()
    async def get_subject_relations(subject_id: int) -> str:
        """
        List related subjects (sequels, prequels, adaptations) for a subject.

        Args:
            subject_id: The ID of the subject.

        Returns:
            Formatted list of related subjects or an error message.
        """
        response = await make_bangumi_request(
            method="GET", path=f"/v0/subjects/{subject_id}/subjects"
        )

        error_msg = handle_api_error_response(response)
        if error_msg:
            return error_msg

        # Expecting a list of related subjects
        if not isinstance(response, list):
            return f"Unexpected API response format for get_subject_relations: {response}"

        related_subjects = response
        if not related_subjects:
            return f"No related subjects found for subject ID {subject_id}."

        formatted_results = []
        for rel_subject in related_subjects:
            name = rel_subject.get("name")
            name_cn = rel_subject.get("name_cn")
            rel_id = rel_subject.get("id")

            # Safely get subject type string
            rel_type_int = rel_subject.get("type")
            rel_type_str = "Unknown Type"
            if rel_type_int is not None:
                try:
                    rel_type_str = SubjectType(rel_type_int).name
                except ValueError:
                    rel_type_str = f"Unknown Type ({rel_type_int})"

            relation = rel_subject.get("relation")

            formatted_results.append(
                f"Subject ID: {rel_id}, Name: {name_cn or name}, Type: {rel_type_str}, Relation: {relation}"
            )

        return "Related Subjects:\n" + "\n---\n".join(formatted_results)

    @mcp.tool()
    async def get_episodes(
        subject_id: int,
        episode_type: Optional[EpType] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> str:
        """
        List episodes for a subject.

        Supported Episode Types (integer enum):
        0: MainStory, 1: SP, 2: OP, 3: ED, 4: PV, 5: MAD, 6: Other

        Args:
            subject_id: The ID of the subject.
            episode_type: Optional filter by episode type (integer value from EpType enum).
            limit: Pagination limit. Max 200. Defaults to 100.
            offset: Pagination offset. Defaults to 0.

        Returns:
            Formatted list of episodes or an error message.
        """
        query_params: Dict[str, Any] = {
            "subject_id": subject_id,
            "limit": min(limit, 200),
            "offset": offset,
        }
        if episode_type is not None:
            query_params["type"] = int(episode_type)

        response = await make_bangumi_request(
            method="GET", path="/v0/episodes", query_params=query_params
        )

        error_msg = handle_api_error_response(response)
        if error_msg:
            return error_msg

        # Expecting a dictionary with 'data' and 'total'
        if not isinstance(response, dict) or "data" not in response:
            return f"Unexpected API response format for get_episodes: {response}"

        episodes = response.get("data", [])
        if not episodes:
            return f"No episodes found for subject ID {subject_id} with the given criteria."

        formatted_results = []
        for ep in episodes:
            ep_id = ep.get("id")
            name = ep.get("name")
            name_cn = ep.get("name_cn")
            sort = ep.get("sort")

            ep_type_int = ep.get("type")
            ep_type_str = "Unknown Type"
            if ep_type_int is not None:
                try:
                    ep_type_str = EpType(ep_type_int).name
                except ValueError:
                    ep_type_str = f"Unknown Type ({ep_type_int})"

            airdate = ep.get("airdate")

            formatted_results.append(
                f"Episode ID: {ep_id}, Type: {ep_type_str}, Number: {sort}, Name: {name_cn or name}, Airdate: {airdate}"
            )

        total = response.get("total", 0)
        results_text = f"Found {len(episodes)} episodes (Total: {total}).\n" + "---\n".join(
            formatted_results
        )

        return results_text

    @mcp.tool()
    async def get_episode_details(episode_id: int) -> str:
        """
        Get details of a specific episode.

        Args:
            episode_id: The ID of the episode.

        Returns:
            Formatted episode details or an error message.
        """
        response = await make_bangumi_request(
            method="GET", path=f"/v0/episodes/{episode_id}"
        )

        error_msg = handle_api_error_response(response)
        if error_msg:
            return error_msg

        # Expecting a dictionary
        if not isinstance(response, dict):
            return f"Unexpected API response format for get_episode_details: {response}"

        episode = response  # Response is the episode dictionary directly

        details_text = f"Episode Details (ID: {episode_id}):\n"
        details_text += f"  Subject ID: {episode.get('subject_id')}\n"
        ep_type_int = episode.get("type")
        ep_type_str = "Unknown Type"
        if ep_type_int is not None:
            try:
                ep_type_str = EpType(ep_type_int).name
            except ValueError:
                ep_type_str = f"Unknown Type ({ep_type_int})"

        details_text += f"  Type: {ep_type_str}\n"
        details_text += f"  Number: {episode.get('sort')}\n"
        if episode.get("ep") is not None:
            details_text += f"  Subject Episode Number: {episode.get('ep')}\n"
        details_text += f"  Name: {episode.get('name')}\n"
        if episode.get("name_cn"):
            details_text += f"  Chinese Name: {episode.get('name_cn')}\n"
        details_text += f"  Airdate: {episode.get('airdate')}\n"
        if episode.get("duration"):
            details_text += f"  Duration: {episode.get('duration')} ({episode.get('duration_seconds', 0)}s)\n"
        if episode.get("disc"):
            details_text += f"  Disc: {episode.get('disc')}\n"
        details_text += f"  Comment Count: {episode.get('comment')}\n"
        details_text += f"  Description:\n{episode.get('desc')}\n"

        return details_text
