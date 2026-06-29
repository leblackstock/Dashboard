import re

from fastapi import HTTPException

from backend.app.db import utc_now_iso
from backend.app.models import (
    BlockedItem,
    BriefSuggestion,
    CollectorHealthItem,
    Project,
    QuickCapture,
    TopItem,
)

BLOCKED_CAPTURE_MARKERS = (
    "access_token",
    "refresh_token",
    "authorization:",
    "bearer ",
    "cookie:",
    "set-cookie:",
    "raw_payload",
    "raw endpoint payload",
    "prompt history",
    "prompt_preview",
    "prompt preview",
    "first user message",
    "rollout-",
    ".jsonl",
    ".codex",
    "-----begin",
)

FULL_PATH_PATTERN = re.compile(r"(?i)(\b[a-z]:\\|\\\\\?\\|\\\\[a-z0-9_.-]+\\|/users/|/home/)")
PROJECT_KEY_PATTERN = re.compile(r"[^a-z0-9]+")


def today_prefix() -> str:
    return utc_now_iso().split("T", maxsplit=1)[0]


def safe_project_key(project_label: str) -> str:
    lowered = project_label.strip().lower()
    key = PROJECT_KEY_PATTERN.sub("-", lowered).strip("-")
    return (key or "project")[:80]


def validate_capture_text(text: str) -> None:
    lowered = text.lower()
    if any(marker in lowered for marker in BLOCKED_CAPTURE_MARKERS):
        raise HTTPException(status_code=400, detail="quick_capture_text_not_allowed")
    if FULL_PATH_PATTERN.search(text):
        raise HTTPException(status_code=400, detail="quick_capture_text_not_allowed")


def project_from_row(row: dict) -> Project:
    return Project(**row)


def top_item_from_row(row: dict) -> TopItem:
    completed_at = row.get("completed_at")
    display_state = "normal"
    if row["status"] == "completed" and completed_at:
        display_state = "completed_today"
    return TopItem(
        id=row["id"],
        title=row["title"],
        project_key=row.get("project_key"),
        project_label=row.get("project_label"),
        reason=row.get("reason"),
        status=row["status"],
        sort_order=row["sort_order"],
        pinned=bool(row["pinned"]),
        source=row.get("source"),
        source_suggestion_key=row.get("source_suggestion_key"),
        source_item_type=row.get("source_item_type"),
        source_label=row.get("source_label"),
        display_state=display_state,
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        completed_at=completed_at,
    )


def brief_suggestion_from_row(row: dict) -> BriefSuggestion:
    return BriefSuggestion(
        id=row["id"],
        source=row["source"],
        source_label=row["source_label"],
        briefing_date=row["briefing_date"],
        source_item_type=row["source_item_type"],
        title=row["title"],
        reason=row.get("reason"),
        project_key=row.get("project_key"),
        project_label=row.get("project_label"),
        urgency=row.get("urgency"),
        source_status=row.get("source_status"),
        status=row["status"],
        imported_at=row["imported_at"],
        updated_at=row["updated_at"],
        accepted_at=row.get("accepted_at"),
        ignored_at=row.get("ignored_at"),
    )


def quick_capture_from_row(row: dict) -> QuickCapture:
    return QuickCapture(
        id=row["id"],
        text=row["text"],
        captured_at=row["captured_at"],
        project_key=row.get("project_key"),
        project_label=row.get("project_label"),
        capture_type=row.get("capture_type"),
        status=row.get("status"),
        processed=bool(row["processed"]),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def blocked_item_from_row(row: dict) -> BlockedItem:
    return BlockedItem(
        id=row["id"],
        project_key=row.get("project_key"),
        project_label=row.get("project_label"),
        title=row["title"],
        reason=row.get("reason"),
        status=row["status"],
        next_action=row.get("next_action"),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        resolved_at=row.get("resolved_at"),
    )


def collector_health_item(
    *,
    collector_name: str,
    label: str,
    latest_status: str,
    last_success_at: str | None,
    last_failed_at: str | None,
    records_written: int,
    safe_message: str,
    freshness: str,
) -> CollectorHealthItem:
    return CollectorHealthItem(
        collector_name=collector_name,
        label=label,
        latest_status=latest_status,
        last_success_at=last_success_at,
        last_failed_at=last_failed_at,
        records_written=records_written,
        safe_message=safe_message,
        freshness=freshness,
    )
