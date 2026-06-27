from fastapi import APIRouter

from backend.app.db import (
    init_db,
    list_blocked_items,
    list_brief_suggestions,
    list_projects,
    list_quick_captures,
    list_top_items_for_daily,
)
from backend.app.models import DailyDashboardResponse
from backend.app.routes.collector_health import get_collector_health_items
from backend.app.routes.serializers import (
    blocked_item_from_row,
    brief_suggestion_from_row,
    project_from_row,
    quick_capture_from_row,
    today_prefix,
    top_item_from_row,
)

router = APIRouter(prefix="/api/daily", tags=["daily"])


@router.get("", response_model=DailyDashboardResponse)
def daily_dashboard() -> DailyDashboardResponse:
    init_db()
    return DailyDashboardResponse(
        projects=[
            project_from_row(row)
            for row in list_projects(statuses=("Active", "Blocked", "Needs Review"))
        ],
        top_items=[
            top_item_from_row(row)
            for row in list_top_items_for_daily(today=today_prefix())
        ],
        brief_suggestions=[
            brief_suggestion_from_row(row)
            for row in list_brief_suggestions(statuses=("pending",), limit=10)
        ],
        blocked_items=[
            blocked_item_from_row(row)
            for row in list_blocked_items(include_resolved=False)
        ],
        quick_captures=[
            quick_capture_from_row(row)
            for row in list_quick_captures(limit=5, include_processed=False)
        ],
        collector_health=get_collector_health_items(),
    )
