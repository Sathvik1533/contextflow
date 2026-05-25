"""Content Parser — Pure Python filter for Observer output.

No LLM. No API. Just rules.

Each content type has different fields that matter to the Guide.
This parser throws away noise so the Guide gets focused input.
"""

from typing import Any


# Fields that matter for each content type
FIELDS_BY_TYPE = {
    "youtube": ["content_type", "title", "primary_text", "url_visible", "confidence"],
    "documentation": ["content_type", "title", "headings", "lists", "primary_text", "code_blocks", "confidence"],
    "code": ["content_type", "title", "code_blocks", "error_messages", "confidence"],
    "error": ["content_type", "error_messages", "code_blocks", "primary_text", "confidence"],
    "other": None,  # None means keep everything
}


def parse_context(extracted_context: dict[str, Any]) -> dict[str, Any]:
    """Filter extracted_context to only the fields relevant for this content type.

    Args:
        extracted_context: Full Observer output dict (10 fields)

    Returns:
        Filtered dict with only relevant fields for this content type.
        Always includes content_type and confidence so downstream nodes
        can still route and check quality.

    Raises:
        ValueError: If extracted_context is empty or missing content_type
    """
    if not extracted_context:
        raise ValueError("parse_context: extracted_context is empty")

    content_type = extracted_context.get("content_type")
    if not content_type:
        raise ValueError("parse_context: missing content_type field")

    # Get the field list for this content type
    # Unknown content_type → treat as "other" (keep everything)
    fields_to_keep = FIELDS_BY_TYPE.get(content_type, None)

    if fields_to_keep is None:
        # "other" or unknown type → return as-is
        return extracted_context

    # Filter: keep only the fields that matter for this content type
    return {
        field: extracted_context.get(field, "" if isinstance(extracted_context.get(field), str) else [])
        for field in fields_to_keep
        if field in extracted_context
    }
