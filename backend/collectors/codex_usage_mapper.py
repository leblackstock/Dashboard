from datetime import UTC, datetime
from typing import Any

from backend.collectors.codex_auth import derive_account_label, sanitize_identity_text

FORBIDDEN_OUTPUT_KEYS = {
    "access_token",
    "refresh_token",
    "cookie",
    "cookies",
    "authorization",
    "authorization_header",
    "auth_header",
    "auth_file",
    "raw_payload",
    "prompt",
    "prompt_preview",
    "first_user_message",
    "raw_log",
    "workspace_path",
}

IDENTITY_CONTAINERS = ("account", "user", "profile", "identity")


def extract_codex_usage_identity(payload: dict[str, Any]) -> dict[str, str | None]:
    candidates = [payload]
    candidates.extend(
        value for key in IDENTITY_CONTAINERS if isinstance((value := payload.get(key)), dict)
    )
    email = next(
        (
            value
            for candidate in candidates
            if (value := candidate.get("email") or candidate.get("preferred_username"))
            is not None
        ),
        None,
    )
    name = next(
        (
            value
            for candidate in candidates
            if (value := candidate.get("name") or candidate.get("display_name")) is not None
        ),
        None,
    )
    safe_name = sanitize_identity_text(name)
    return {
        "account_label": derive_account_label(email, safe_name),
        "account_name": safe_name,
    }


def compute_freshness(collected_at: str | None = None) -> str:
    if not collected_at:
        return "unknown"
    try:
        parsed = datetime.fromisoformat(collected_at.replace("Z", "+00:00"))
    except ValueError:
        return "unknown"
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    age_hours = (datetime.now(UTC) - parsed.astimezone(UTC)).total_seconds() / 3600
    if age_hours < 2:
        return "fresh"
    if age_hours < 6:
        return "slightly_stale"
    if age_hours < 24:
        return "stale"
    return "very_stale"


def _walk_values(value: Any) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    if isinstance(value, dict):
        found.append(value)
        for child in value.values():
            found.extend(_walk_values(child))
    elif isinstance(value, list):
        for item in value:
            found.extend(_walk_values(item))
    return found


def _first_present(payload: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for item in _walk_values(payload):
        for key in keys:
            if key in item and item[key] is not None:
                return item[key]
    return None


def _number(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        stripped = value.strip().removesuffix("%")
        try:
            return float(stripped)
        except ValueError:
            return None
    return None


def _int_or_none(value: Any) -> int | None:
    number = _number(value)
    if number is None:
        return None
    return int(number)


def _iso_from_unix_timestamp(value: int | float) -> str:
    return datetime.fromtimestamp(value, UTC).replace(microsecond=0).isoformat()


def _percent_pair(item: dict[str, Any]) -> tuple[float | None, float | None]:
    used = _number(
        _first_direct(
            item,
            (
                "used_percent",
                "percent_used",
                "usedPercentage",
                "usage_percent",
                "usagePercent",
            ),
        )
    )
    remaining = _number(
        _first_direct(
            item,
            (
                "remaining_percent",
                "percent_remaining",
                "remainingPercentage",
                "remaining_percent_available",
                "remainingPercent",
            ),
        )
    )
    if used is None and remaining is not None:
        used = max(0.0, min(100.0, 100.0 - remaining))
    if remaining is None and used is not None:
        remaining = max(0.0, min(100.0, 100.0 - used))
    return used, remaining


def _first_direct(item: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        if key in item and item[key] is not None:
            return item[key]
    return None


def _window_token(item: dict[str, Any]) -> str:
    values = [
        item.get("window"),
        item.get("window_label"),
        item.get("windowLabel"),
        item.get("limit_window"),
        item.get("limitWindow"),
        item.get("name"),
        item.get("label"),
        item.get("type"),
    ]
    return " ".join(str(value).lower() for value in values if value is not None)


def _window_minutes(item: dict[str, Any]) -> int | None:
    minute_value = _first_direct(
        item,
        (
            "window_minutes",
            "windowMinutes",
            "duration_minutes",
            "durationMinutes",
            "period_minutes",
            "periodMinutes",
        ),
    )
    minutes = _int_or_none(minute_value)
    if minutes is not None:
        return minutes

    second_value = _first_direct(
        item,
        (
            "window_seconds",
            "windowSeconds",
            "limit_window_seconds",
            "limitWindowSeconds",
            "duration_seconds",
            "durationSeconds",
            "period_seconds",
            "periodSeconds",
        ),
    )
    seconds = _int_or_none(second_value)
    if seconds is None:
        return None
    return int(seconds / 60)


def _find_window(
    payload: dict[str, Any],
    *,
    minutes: int,
    labels: tuple[str, ...],
) -> dict[str, Any] | None:
    for item in _walk_values(payload):
        if _window_minutes(item) == minutes:
            return item
        token = _window_token(item)
        if token and any(label in token for label in labels):
            return item
    return None


def _reset_at(item: dict[str, Any] | None) -> str | None:
    if not item:
        return None
    value = _first_direct(
        item,
        (
            "reset_at",
            "resetAt",
            "resets_at",
            "resetsAt",
            "next_reset_at",
            "nextResetAt",
        ),
    )
    if isinstance(value, int | float):
        return _iso_from_unix_timestamp(value)
    return str(value) if value is not None else None


def map_codex_usage_payload(
    payload: dict[str, Any],
    *,
    account_key_hash: str,
    account_label: str | None,
    account_name: str | None,
    collected_at: str,
) -> dict[str, Any]:
    quota_5h = _find_window(payload, minutes=300, labels=("5h", "5-hour", "300"))
    quota_weekly = _find_window(payload, minutes=10080, labels=("weekly", "week", "10080"))

    if quota_5h is None:
        quota_5h = payload
    if quota_weekly is None:
        quota_weekly = payload

    quota_5h_used, quota_5h_remaining = _percent_pair(quota_5h)
    weekly_used, weekly_remaining = _percent_pair(quota_weekly)

    snapshot = {
        "provider": "openai",
        "tool": "codex",
        "account_key_hash": account_key_hash,
        "account_label": account_label,
        "account_name": account_name,
        "plan_type": _first_present(
            payload,
            ("plan_type", "planType", "plan", "subscription_plan"),
        ),
        "reset_credits_available": _int_or_none(
            _first_present(
                payload,
                (
                    "reset_credits_available",
                    "resetCreditsAvailable",
                    "resets_available",
                    "resetsAvailable",
                    "available_count",
                    "availableCount",
                ),
            )
        ),
        "quota_5h_used_percent": quota_5h_used,
        "quota_5h_remaining_percent": quota_5h_remaining,
        "quota_5h_reset_at": _reset_at(quota_5h),
        "quota_weekly_used_percent": weekly_used,
        "quota_weekly_remaining_percent": weekly_remaining,
        "quota_weekly_reset_at": _reset_at(quota_weekly),
        "session_count": 1,
        "source_type": "official_endpoint",
        "source_label": "chatgpt_backend_wham_usage",
        "confidence": "high",
        "freshness": compute_freshness(collected_at),
        "collected_at": collected_at,
    }
    return _without_forbidden_keys(snapshot)


def _without_forbidden_keys(snapshot: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in snapshot.items()
        if key.lower() not in FORBIDDEN_OUTPUT_KEYS
    }
