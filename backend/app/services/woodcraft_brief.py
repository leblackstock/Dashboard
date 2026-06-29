import hashlib
import json
import re
from pathlib import Path
from typing import Any

from backend.app.brief_dedupe import normalized_brief_action_key
from backend.app.db import (
    ensure_project,
    get_project,
    hide_duplicate_pending_brief_suggestions,
    insert_brief_suggestion,
    resolve_repo_path,
)
from backend.app.routes.serializers import BLOCKED_CAPTURE_MARKERS, FULL_PATH_PATTERN

BRIEF_SOURCE = "woodcraft_brief_me"
BRIEF_SOURCE_LABEL = "Woodcraft Brief Me"
DEFAULT_PROJECT_KEY = "woodcraft"
DEFAULT_PROJECT_LABEL = "Woodcraft Workspace"
PROJECT_KEY_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{0,79}$")


class BriefImportError(Exception):
    def __init__(self, safe_message: str) -> None:
        super().__init__(safe_message)
        self.safe_message = safe_message


def import_woodcraft_brief_suggestions(
    *,
    source_path: Path | None,
) -> dict[str, int | str]:
    payload = _load_brief_payload(source_path)
    suggestions = _extract_suggestions(payload)

    imported = 0
    already_imported = 0
    skipped = 0
    current_action_keys: set[str] = set()
    current_suggestion_keys: set[str] = set()

    for suggestion in suggestions:
        if suggestion is None:
            skipped += 1
            continue
        current_action_keys.add(normalized_brief_action_key(suggestion))
        current_suggestion_keys.add(suggestion["suggestion_key"])
        if insert_brief_suggestion(suggestion):
            imported += 1
        else:
            already_imported += 1
    duplicates_hidden = hide_duplicate_pending_brief_suggestions(
        current_action_keys=current_action_keys,
        current_suggestion_keys=current_suggestion_keys
    )

    return {
        "status": "success",
        "imported": imported,
        "already_imported": already_imported,
        "skipped": skipped,
        "duplicates_hidden": duplicates_hidden,
        "safe_message": "brief_suggestions_imported",
    }


def _load_brief_payload(source_path: Path | None) -> dict[str, Any]:
    if source_path is None:
        raise BriefImportError("brief_source_not_configured")
    resolved = resolve_repo_path(source_path).resolve()
    if not resolved.is_file():
        raise BriefImportError("brief_source_not_available")
    try:
        payload = json.loads(resolved.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BriefImportError("brief_source_unreadable") from exc
    if not isinstance(payload, dict):
        raise BriefImportError("brief_source_invalid")
    if payload.get("source") != BRIEF_SOURCE:
        raise BriefImportError("brief_source_invalid")
    required_keys = (
        "briefing_date",
        "timezone",
        "state",
        "priorities",
        "next_actions",
        "project_status",
    )
    for key in required_keys:
        if key not in payload:
            raise BriefImportError("brief_source_invalid")
    if not isinstance(payload["priorities"], list) or not isinstance(payload["next_actions"], list):
        raise BriefImportError("brief_source_invalid")
    return payload


def _extract_suggestions(payload: dict[str, Any]) -> list[dict[str, Any] | None]:
    briefing_date = _clean_text(payload.get("briefing_date"), max_length=40)
    if briefing_date is None:
        raise BriefImportError("brief_source_invalid")

    suggestions: list[dict[str, Any] | None] = []
    for item_type, items in (
        ("priority", payload["priorities"]),
        ("next_action", payload["next_actions"]),
    ):
        for index, item in enumerate(items):
            suggestions.append(_suggestion_from_item(item, item_type, index, briefing_date))
    return suggestions


def _suggestion_from_item(
    item: Any,
    item_type: str,
    index: int,
    briefing_date: str,
) -> dict[str, Any] | None:
    if not isinstance(item, dict):
        return None

    title = _clean_text(item.get("title"), max_length=200)
    if title is None:
        return None

    reason = _clean_text(item.get("reason"), max_length=500)
    project_key = _safe_project_key(item.get("project_key"))
    urgency = _clean_text(item.get("urgency"), max_length=60)
    source_status = _clean_text(item.get("status"), max_length=60)

    suggestion = {
        "source": BRIEF_SOURCE,
        "source_label": BRIEF_SOURCE_LABEL,
        "briefing_date": briefing_date,
        "source_item_type": item_type,
        "source_item_index": index,
        "title": title,
        "reason": reason,
        "project_key": project_key,
        "urgency": urgency,
        "source_status": source_status,
        "status": "pending",
    }
    suggestion["suggestion_key"] = _suggestion_key(suggestion)
    return suggestion


def _clean_text(value: Any, *, max_length: int) -> str | None:
    if not isinstance(value, str):
        return None
    cleaned = " ".join(value.strip().split())
    if not cleaned:
        return None
    lowered = cleaned.lower()
    if any(marker in lowered for marker in BLOCKED_CAPTURE_MARKERS):
        return None
    if FULL_PATH_PATTERN.search(cleaned):
        return None
    return cleaned[:max_length]


def _safe_project_key(value: Any) -> str:
    if isinstance(value, str):
        project_key = value.strip().lower()
        if PROJECT_KEY_PATTERN.fullmatch(project_key) and get_project(project_key) is not None:
            return project_key
    ensure_project(
        project_key=DEFAULT_PROJECT_KEY,
        project_label=DEFAULT_PROJECT_LABEL,
        priority=45,
        safe_notes="Default project for sanitized Woodcraft Brief Me suggestions.",
    )
    return DEFAULT_PROJECT_KEY


def _suggestion_key(suggestion: dict[str, Any]) -> str:
    key_parts = [
        suggestion["source"],
        suggestion["briefing_date"],
        suggestion["source_item_type"],
        suggestion["title"].casefold(),
        (suggestion.get("reason") or "").casefold(),
        suggestion.get("project_key") or "",
        suggestion.get("urgency") or "",
        suggestion.get("source_status") or "",
    ]
    digest = hashlib.sha256("\n".join(key_parts).encode("utf-8")).hexdigest()
    return f"{BRIEF_SOURCE}:{digest[:32]}"
