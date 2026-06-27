import json
from pathlib import Path

from backend.collectors.codex_usage_mapper import FORBIDDEN_OUTPUT_KEYS, map_codex_usage_payload


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
