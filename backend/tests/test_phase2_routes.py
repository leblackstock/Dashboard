import pytest
from fastapi import HTTPException

from backend.app import db as db_module
from backend.app.db import (
    create_blocked_item,
    create_quick_capture,
    create_top_item,
    init_db,
    record_collector_run,
)
from backend.app.models import QuickCaptureCreate
from backend.app.routes.collector_health import collector_health
from backend.app.routes.daily import daily_dashboard
from backend.app.routes.quick_captures import create_quick_capture_endpoint
from backend.app.routes.top_items import top_items
from backend.app.settings import get_settings


def use_temp_db(tmp_path, monkeypatch):
    db_path = tmp_path / "dashboard.db"
    monkeypatch.setenv("DASHBOARD_DB_PATH", str(db_path))
    get_settings.cache_clear()
    init_db(db_path)
    return db_path


def test_top_items_show_open_and_today_completed_only(tmp_path, monkeypatch):
    db_path = use_temp_db(tmp_path, monkeypatch)
    today = db_module.utc_now_iso().split("T", maxsplit=1)[0]

    create_top_item({"title": "Keep working", "status": "active"}, db_path=db_path)
    create_top_item(
        {
            "title": "Finished today",
            "status": "completed",
            "completed_at": f"{today}T12:00:00+00:00",
        },
        db_path=db_path,
    )
    create_top_item(
        {
            "title": "Finished before today",
            "status": "completed",
            "completed_at": "2026-01-01T12:00:00+00:00",
        },
        db_path=db_path,
    )

    response = top_items().model_dump()
    titles = [item["title"] for item in response["items"]]
    completed_today = next(item for item in response["items"] if item["title"] == "Finished today")

    assert titles == ["Keep working", "Finished today"]
    assert completed_today["display_state"] == "completed_today"


def test_quick_capture_accepts_notes_and_rejects_sensitive_dumps(tmp_path, monkeypatch):
    use_temp_db(tmp_path, monkeypatch)

    saved = create_quick_capture_endpoint(
        QuickCaptureCreate(text="Remember to review the dashboard card spacing.")
    )

    assert saved.text == "Remember to review the dashboard card spacing."

    blocked_marker = "access" + "_token=do-not-store"
    with pytest.raises(HTTPException) as exc_info:
        create_quick_capture_endpoint(QuickCaptureCreate(text=blocked_marker))

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "quick_capture_text_not_allowed"


def test_collector_health_reports_latest_safe_status(tmp_path, monkeypatch):
    db_path = use_temp_db(tmp_path, monkeypatch)
    record_collector_run(
        collector_name="codex_live_usage",
        started_at="2026-06-27T12:00:00+00:00",
        finished_at="2026-06-27T12:00:01+00:00",
        status="success",
        safe_message="codex_usage_collected",
        records_written=1,
        db_path=db_path,
    )

    response = collector_health().model_dump()
    item = response["collectors"][0]

    assert item["collector_name"] == "codex_live_usage"
    assert item["latest_status"] == "success"
    assert item["last_success_at"] == "2026-06-27T12:00:01+00:00"
    assert item["safe_message"] == "codex_usage_collected"


def test_daily_dashboard_returns_phase2_card_data(tmp_path, monkeypatch):
    db_path = use_temp_db(tmp_path, monkeypatch)
    create_top_item({"title": "Plan the day", "status": "active"}, db_path=db_path)
    create_blocked_item({"title": "Needs review", "status": "Needs Review"}, db_path=db_path)
    create_quick_capture({"text": "Local idea only"}, db_path=db_path)

    response = daily_dashboard().model_dump()

    assert response["projects"]
    assert response["top_items"][0]["title"] == "Plan the day"
    assert response["blocked_items"][0]["title"] == "Needs review"
    assert response["quick_captures"][0]["text"] == "Local idea only"
    assert response["collector_health"][0]["collector_name"] == "codex_live_usage"
