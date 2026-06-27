from sqlite3 import Row

from fastapi import APIRouter

from backend.app.db import init_db, latest_codex_usage_rows
from backend.app.models import CodexUsageAccount, CodexUsageResponse, QuotaWindow
from backend.collectors.codex_usage_mapper import compute_freshness

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


@router.get("/live-usage", response_model=CodexUsageResponse)
def live_usage() -> CodexUsageResponse:
    return get_live_usage_response()
