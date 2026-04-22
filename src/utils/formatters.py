"""Formatting utilities for Bangumi data structures."""
from typing import Any, Dict

from enums import SubjectType, CharacterType, PersonType


def format_subject_summary(subject: Dict[str, Any]) -> str:
    """Formats a subject dictionary into a readable summary string."""
    name = subject.get("name")
    name_cn = subject.get("name_cn")
    subject_type = subject.get("type")
    subject_id = subject.get("id")
    score = subject.get("rating", {}).get("score")  # Access Nested Score
    rank = subject.get("rating", {}).get("rank")  # Access Nested Rank
    summary = subject.get("short_summary") or subject.get("summary", "")

    try:
        type_str = (
            SubjectType(subject_type).name
            if subject_type is not None
            else "Unknown Type"
        )
    except ValueError:
        type_str = f"Unknown Type ({subject_type})"

    formatted_string = f"[{type_str}] {name_cn or name} (ID: {subject_id})\n"
    if score is not None:
        formatted_string += f"  Score: {score}\n"
    if rank is not None:
        formatted_string += f"  Rank: {rank}\n"
    if summary:
        formatted_summary = summary  # [:200] + '...' if len(summary) > 200 else summary
        formatted_string += f"  Summary: {formatted_summary}\n"

    # Add images URL if available (for potential LLM multi-modal future use or user info)
    images = subject.get("images")
    if images and images.get("common"):
        formatted_string += f"  Image: {images.get('common')}\n"  # Or 'grid', 'large', 'medium', 'small' depending on preference

    return formatted_string


def format_character_summary(character: Dict[str, Any]) -> str:
    """Formats a character dictionary into a readable summary string."""
    character_id = character.get("id")
    name = character.get("name")
    char_type = character.get("type")  # Integer enum
    summary = character.get("short_summary") or character.get("summary", "")

    try:
        type_str = (
            CharacterType(char_type).name if char_type is not None else "Unknown Type"
        )
    except ValueError:
        type_str = f"Unknown Type ({char_type})"

    formatted_string = f"[{type_str}] {name} (ID: {character_id})\n"
    if summary:
        formatted_summary = summary  # [:200] + '...' if len(summary) > 200 else summary
        formatted_string += f"  Summary: {formatted_summary}\n"

    images = character.get("images")
    if images and images.get("common"):
        formatted_string += f"  Image: {images.get('common')}\n"

    return formatted_string


def format_person_summary(person: Dict[str, Any]) -> str:
    """Formats a person dictionary into a readable summary string."""
    person_id = person.get("id")
    name = person.get("name")
    person_type = person.get("type")  # Integer enum
    career = person.get("career")  # List of string enums
    summary = person.get("short_summary") or person.get("summary", "")

    try:
        type_str = (
            PersonType(person_type).name if person_type is not None else "Unknown Type"
        )
    except ValueError:
        type_str = f"Unknown Type ({person_type})"

    formatted_string = f"[{type_str}] {name} (ID: {person_id})\n"
    if career:
        formatted_string += f"  Career: {', '.join(career)}\n"
    if summary:
        formatted_summary = summary  # [:200] + '...' if len(summary) > 200 else summary
        formatted_string += f"  Summary: {formatted_summary}\n"

    images = person.get("images")
    if images and images.get("common"):
        formatted_string += f"  Image: {images.get('common')}\n"

    return formatted_string
