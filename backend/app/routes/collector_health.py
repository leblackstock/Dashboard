from fastapi import APIRouter

from backend.app.db import init_db, latest_collector_run
from backend.app.models import CollectorHealthItem, CollectorHealthResponse
from backend.app.routes.serializers import collector_health_item
from backend.collectors.codex_usage_mapper import compute_freshness

router = APIRouter(prefix="/api/collectors", tags=["collectors"])

TRACKED_COLLECTORS = (
    {
        "collector_name": "codex_live_usage",
        "label": "Codex live usage",
    },
)


def get_collector_health_items() -> list[CollectorHealthItem]:
    init_db()
    items: list[CollectorHealthItem] = []
    for collector in TRACKED_COLLECTORS:
        collector_name = collector["collector_name"]
        latest = latest_collector_run(collector_name)
        latest_success = latest_collector_run(collector_name, status="success")
        latest_failed = latest_collector_run(collector_name, status="failed")

        if latest is None:
            items.append(
                collector_health_item(
                    collector_name=collector_name,
                    label=collector["label"],
                    latest_status="never_run",
                    last_success_at=None,
                    last_failed_at=None,
                    records_written=0,
                    safe_message="collector_not_run",
                    freshness="unavailable",
                )
            )
            continue

        finished_at = latest["finished_at"]
        items.append(
            collector_health_item(
                collector_name=collector_name,
                label=collector["label"],
                latest_status=latest["status"],
                last_success_at=latest_success["finished_at"] if latest_success else None,
                last_failed_at=latest_failed["finished_at"] if latest_failed else None,
                records_written=latest["records_written"],
                safe_message=latest["safe_message"],
                freshness=compute_freshness(finished_at),
            )
        )
    return items


@router.get("/health", response_model=CollectorHealthResponse)
def collector_health() -> CollectorHealthResponse:
    return CollectorHealthResponse(collectors=get_collector_health_items())
