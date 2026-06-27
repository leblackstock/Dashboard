from backend.app.db import init_db, insert_usage_snapshot, latest_codex_usage_rows, upsert_account


def test_db_insert_and_latest_snapshot(tmp_path):
    db_path = tmp_path / "dashboard.db"
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
            "collected_at": "2026-06-27T16:00:00+00:00",
        },
        db_path=db_path,
    )

    rows = latest_codex_usage_rows(db_path)
    assert len(rows) == 1
    assert rows[0]["account_key_hash"] == "hash-123"
    assert rows[0]["account_label"] == "local@example.test"
    assert rows[0]["quota_5h_used_percent"] == 34.5
