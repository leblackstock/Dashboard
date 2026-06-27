import json
import sqlite3

from backend.app.routes.ai_codex import get_live_usage_response
from backend.app.settings import get_settings
from backend.collectors import collect_codex_live_usage as collector_module
from backend.collectors.codex_auth import CodexAuth


def test_collector_prefers_live_sanitized_identity_and_never_persists_secrets(
    tmp_path, monkeypatch
):
    db_path = tmp_path / "dashboard.db"
    sanitized_dir = tmp_path / "sanitized"
    monkeypatch.setenv("DASHBOARD_DB_PATH", str(db_path))
    monkeypatch.setenv("DASHBOARD_SANITIZED_DIR", str(sanitized_dir))
    get_settings.cache_clear()

    secret = "fake-access-secret-value"
    auth = CodexAuth(
        access_token=secret,
        account_key_hash="safe-account-hash",
        account_label="auth-label",
        account_name="Auth Name",
        auth_mode="codex_auth",
    )
    payload = {
        "email": "live-label@example.test",
        "name": "Live Name",
        "plan_type": "plus",
        "quotas": [
            {
                "window_minutes": 300,
                "used_percent": 25,
                "reset_at": "2026-06-27T20:00:00+00:00",
            },
            {
                "window_minutes": 10080,
                "used_percent": 50,
                "reset_at": "2026-07-01T00:00:00+00:00",
            },
        ],
    }
    monkeypatch.setattr(collector_module, "load_codex_auth", lambda: auth)
    monkeypatch.setattr(collector_module, "_fetch_usage_payload", lambda _token: payload)

    result = collector_module.collect_codex_live_usage()

    assert result["status"] == "success"
    assert secret not in json.dumps(result, sort_keys=True)
    snapshot = json.loads(
        (sanitized_dir / "codex" / "latest.json").read_text(encoding="utf-8")
    )
    assert snapshot["account_label"] == "live-label"
    assert snapshot["account_name"] == "Live Name"
    assert payload["email"] not in json.dumps(snapshot, sort_keys=True)

    with sqlite3.connect(db_path) as connection:
        account_row = connection.execute(
            "SELECT account_label, account_name FROM ai_accounts WHERE account_key_hash = ?",
            (auth.account_key_hash,),
        ).fetchone()
        database_dump = "\n".join(connection.iterdump())
    assert account_row == ("live-label", "Live Name")
    assert secret not in database_dump
    assert payload["email"] not in database_dump

    response = get_live_usage_response().model_dump()
    assert response["accounts"][0]["account_label"] == "live-label"
    serialized = json.dumps(response, sort_keys=True)
    assert secret not in serialized
    assert payload["email"] not in serialized
    assert all(
        term not in serialized.lower()
        for term in ("access_token", "refresh_token", "id_token", "authorization", "raw_payload")
    )
    get_settings.cache_clear()
