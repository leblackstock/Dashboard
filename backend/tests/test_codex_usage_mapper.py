import json
from datetime import UTC, datetime
from pathlib import Path

from backend.collectors.codex_usage_mapper import (
    FORBIDDEN_OUTPUT_KEYS,
    extract_codex_usage_identity,
    map_codex_usage_payload,
)


def test_usage_identity_extracts_sanitized_label_from_fixture():
    identity = json.loads(
        Path("backend/tests/fixtures/fake_codex_identity.json").read_text(encoding="utf-8")
    )

    result = extract_codex_usage_identity(identity)

    assert result == {
        "account_label": "local",
        "account_name": "Local Test",
    }
    serialized = json.dumps(result, sort_keys=True)
    assert identity["email"] not in serialized
    assert all(term not in serialized.lower() for term in FORBIDDEN_OUTPUT_KEYS)


def test_mapper_outputs_sanitized_fields_only():
    payload = json.loads(
        Path("backend/tests/fixtures/fake_wham_usage.json").read_text(encoding="utf-8")
    )
    snapshot = map_codex_usage_payload(
        payload,
        account_key_hash="hash-123",
        account_label="local@example.test",
        account_name="Local Test",
        collected_at="2026-06-27T16:00:00+00:00",
    )

    assert snapshot["provider"] == "openai"
    assert snapshot["tool"] == "codex"
    assert snapshot["plan_type"] == "plus"
    assert snapshot["reset_credits_available"] == 2
    assert snapshot["quota_5h_used_percent"] == 34.5
    assert snapshot["quota_5h_remaining_percent"] == 65.5
    assert snapshot["quota_weekly_used_percent"] == 12
    assert snapshot["quota_weekly_remaining_percent"] == 88
    assert snapshot["source_label"] == "chatgpt_backend_wham_usage"

    lowered_keys = {key.lower() for key in snapshot}
    assert not lowered_keys.intersection(FORBIDDEN_OUTPUT_KEYS)


def test_mapper_supports_rate_limit_windows_from_live_shape():
    primary_reset = 1_800_000_000
    secondary_reset = 1_800_604_800
    payload = {
        "plan_type": "plus",
        "rate_limit": {
            "primary_window": {
                "used_percent": 22,
                "limit_window_seconds": 18_000,
                "reset_at": primary_reset,
            },
            "secondary_window": {
                "used_percent": 44,
                "limit_window_seconds": 604_800,
                "reset_at": secondary_reset,
            },
        },
        "rate_limit_reset_credits": {
            "available_count": 3,
        },
    }

    snapshot = map_codex_usage_payload(
        payload,
        account_key_hash="hash-123",
        account_label="local@example.test",
        account_name="Local Test",
        collected_at="2026-06-27T16:00:00+00:00",
    )

    assert snapshot["plan_type"] == "plus"
    assert snapshot["reset_credits_available"] == 3
    assert snapshot["quota_5h_used_percent"] == 22
    assert snapshot["quota_5h_remaining_percent"] == 78
    assert snapshot["quota_5h_reset_at"] == datetime.fromtimestamp(primary_reset, UTC).isoformat()
    assert snapshot["quota_weekly_used_percent"] == 44
    assert snapshot["quota_weekly_remaining_percent"] == 56
    assert snapshot["quota_weekly_reset_at"] == datetime.fromtimestamp(
        secondary_reset, UTC
    ).isoformat()
