from sqlite3 import Row

from fastapi import APIRouter

from backend.app.db import init_db, latest_codex_usage_rows
from backend.app.models import (
    CodexCollectResponse,
    CodexUsageAccount,
    CodexUsageResponse,
    QuotaWindow,
)
from backend.collectors.codex_usage_mapper import compute_freshness
from backend.collectors.collect_codex_live_usage import collect_codex_live_usage

router = APIRouter(prefix="/api/ai/codex", tags=["ai-codex"])


def row_to_account(row: Row) -> CodexUsageAccount:
    collected_at = row["collected_at"]
    return CodexUsageAccount(
        account_key_hash=row["account_key_hash"],
        account_label=row["account_label"],
        account_name=row["account_name"],
        plan_type=row["plan_type"],
        reset_credits_available=row["reset_credits_available"],
        quota_5h=QuotaWindow(
            used_percent=row["quota_5h_used_percent"],
            remaining_percent=row["quota_5h_remaining_percent"],
            reset_at=row["quota_5h_reset_at"],
        ),
        quota_weekly=QuotaWindow(
            used_percent=row["quota_weekly_used_percent"],
            remaining_percent=row["quota_weekly_remaining_percent"],
            reset_at=row["quota_weekly_reset_at"],
        ),
        freshness=compute_freshness(collected_at),
        confidence=row["confidence"],
        collected_at=collected_at,
    )


def get_live_usage_response() -> CodexUsageResponse:
    init_db()
    return CodexUsageResponse(accounts=[row_to_account(row) for row in latest_codex_usage_rows()])


def collect_response_from_result(result: dict) -> CodexCollectResponse:
    status = "success" if result.get("status") == "success" else "failed"
    collected_at_value = result.get("collected_at")
    collected_at = collected_at_value if isinstance(collected_at_value, str) else None
    safe_message = public_safe_message(result.get("safe_message"), status=status)
    message = public_user_message(safe_message, status=status)
    return CodexCollectResponse(
        status=status,
        records_written=int(result.get("records_written", 0)),
        collected_at=collected_at,
        last_updated=collected_at if status == "success" else None,
        safe_message=safe_message,
        message=message,
    )


def public_safe_message(value: object, *, status: str) -> str:
    if status == "success":
        return "codex_usage_collected"
    if isinstance(value, str) and value.startswith("auth_failed"):
        return "codex_auth_refresh_failed"
    if isinstance(value, str) and value.startswith("usage_request_failed"):
        return "codex_usage_request_failed"
    return "codex_usage_refresh_failed"


def public_user_message(safe_message: str, *, status: str) -> str:
    if status == "success":
        return "Codex usage refreshed."
    if safe_message == "codex_auth_refresh_failed":
        return "Codex usage could not be refreshed. Check local Codex auth."
    return "Codex usage could not be refreshed. Try again later."


@router.get("/live-usage", response_model=CodexUsageResponse)
def live_usage() -> CodexUsageResponse:
    return get_live_usage_response()


@router.post("/collect", response_model=CodexCollectResponse)
def collect_usage() -> CodexCollectResponse:
    return collect_response_from_result(collect_codex_live_usage())
