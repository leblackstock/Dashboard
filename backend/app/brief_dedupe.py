import re
import unicodedata
from collections.abc import Mapping
from typing import Any

ACTION_TEXT_PATTERN = re.compile(r"[^\w]+", re.UNICODE)


def normalize_brief_action_text(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    normalized = unicodedata.normalize("NFKC", value).casefold()
    normalized = ACTION_TEXT_PATTERN.sub(" ", normalized)
    return " ".join(normalized.split())


def normalized_brief_action_key(row: Mapping[str, Any]) -> str:
    source = normalize_brief_action_text(row.get("source"))
    project_key = normalize_brief_action_text(row.get("project_key"))
    title = normalize_brief_action_text(row.get("title"))
    return "\n".join((source, project_key, title))
