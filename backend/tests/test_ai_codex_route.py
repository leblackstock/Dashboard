from backend.app import db as db_module
from backend.app.db import init_db, insert_usage_snapshot, upsert_account
from backend.app.routes import ai_codex
from backend.app.routes.ai_codex import collect_usage, get_live_usage_response
from backend.app.settings import get_settings


def test_api_response_contains_sanitized_shape(tmp_path, monkeypatch):
    db_path = tmp_path / "dashboard.db"
    monkeypatch.setenv("DASHBOARD_DB_PATH", str(db_path))
    get_settings.cache_clear()
    init_db(db_path)
    upsert_account(
        {
            "provider": "openai",
            "account_key_hash": "hash-123",
            "account_label": "local@example.test",
            "account_name": "Local Test",
            "auth_mode": "codex_auth",
        },
        db_path=db_path,
    )
    insert_usage_snapshot(
        {
            "provider": "openai",
            "tool": "codex",
            "account_key_hash": "hash-123",
            "plan_type": "plus",
            "reset_credits_available": 2,
            "quota_5h_used_percent": 34.5,
            "quota_5h_remaining_percent": 65.5,
            "quota_5h_reset_at": "2026-06-27T18:00:00+00:00",
            "quota_weekly_used_percent": 12,
            "quota_weekly_remaining_percent": 88,
            "quota_weekly_reset_at": "2026-07-01T00:00:00+00:00",
            "session_count": 1,
            "source_type": "official_endpoint",
            "source_label": "chatgpt_backend_wham_usage",
            "confidence": "high",
            "freshness": "fresh",
            "collected_at": db_module.utc_now_iso(),
        },
        db_path=db_path,
    )

    response = get_live_usage_response().model_dump()

    assert response["accounts"][0]["account_key_hash"] == "hash-123"
    assert response["accounts"][0]["quota_5h"]["used_percent"] == 34.5
    serialized = str(response).lower()
    forbidden_terms = ["access_token", "refresh_token", "authorization", "raw_payload"]
    assert all(term not in serialized for term in forbidden_terms)


def test_collect_endpoint_returns_sanitized_success(monkeypatch):
    def fake_collector():
        return {
            "status": "success",
            "records_written": 1,
            "snapshot_file": "latest.json",
            "collected_at": "2026-06-27T16:00:00+00:00",
        }

    monkeypatch.setattr(ai_codex, "collect_codex_live_usage", fake_collector)

    response = collect_usage().model_dump()

    assert response == {
        "status": "success",
        "records_written": 1,
        "collected_at": "2026-06-27T16:00:00+00:00",
        "last_updated": "2026-06-27T16:00:00+00:00",
        "safe_message": "codex_usage_collected",
        "message": "Codex usage refreshed.",
    }
    serialized = str(response).lower()
    forbidden_terms = ["snapshot_file", "access_token", "authorization", "raw_payload"]
    assert all(term not in serialized for term in forbidden_terms)


def test_collect_endpoint_returns_safe_auth_failure(monkeypatch):
    def fake_collector():
        return {
            "status": "failed",
            "records_written": 0,
            "safe_message": "auth_failed:codex_auth_not_found",
        }

    monkeypatch.setattr(ai_codex, "collect_codex_live_usage", fake_collector)

    response = collect_usage().model_dump()

    assert response == {
        "status": "failed",
        "records_written": 0,
        "collected_at": None,
        "last_updated": None,
        "safe_message": "codex_auth_refresh_failed",
        "message": "Codex usage could not be refreshed. Check local Codex auth.",
    }
    serialized = str(response).lower()
    forbidden_terms = ["auth.json", "access_token", "refresh_token", "authorization"]
    assert all(term not in serialized for term in forbidden_terms)
