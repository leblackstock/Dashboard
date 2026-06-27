import argparse
import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from backend.app.db import (
    init_db,
    insert_usage_snapshot,
    record_collector_run,
    resolve_repo_path,
    upsert_account,
    utc_now_iso,
)
from backend.app.settings import get_settings
from backend.collectors.codex_auth import CodexAuthError, load_codex_auth
from backend.collectors.codex_usage_mapper import map_codex_usage_payload

COLLECTOR_NAME = "codex_live_usage"
USAGE_ENDPOINT = "https://chatgpt.com/backend-api/wham/usage"


def collect_codex_live_usage() -> dict[str, Any]:
    started_at = utc_now_iso()
    init_db()

    try:
        auth = load_codex_auth()
        payload = _fetch_usage_payload(auth.access_token)
        collected_at = utc_now_iso()
        snapshot = map_codex_usage_payload(
            payload,
            account_key_hash=auth.account_key_hash,
            account_label=auth.account_label,
            account_name=auth.account_name,
            collected_at=collected_at,
        )
        upsert_account(auth.safe_account_metadata())
        insert_usage_snapshot(snapshot)
        snapshot_file = write_sanitized_snapshot(snapshot)
        finished_at = utc_now_iso()
        record_collector_run(
            collector_name=COLLECTOR_NAME,
            started_at=started_at,
            finished_at=finished_at,
            status="success",
            safe_message="codex_usage_collected",
            records_written=1,
        )
        return {
            "status": "success",
            "records_written": 1,
            "snapshot_file": snapshot_file.name,
            "collected_at": collected_at,
        }
    except CodexAuthError as exc:
        return _record_failure(started_at, f"auth_failed:{exc}")
    except (urllib.error.URLError, TimeoutError) as exc:
        return _record_failure(started_at, f"usage_request_failed:{type(exc).__name__}")
    except Exception as exc:
        return _record_failure(started_at, f"collector_failed:{type(exc).__name__}")


def _fetch_usage_payload(access_token: str) -> dict[str, Any]:
    request = urllib.request.Request(
        USAGE_ENDPOINT,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        },
        method="GET",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read()
    payload = json.loads(body.decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("unexpected_usage_payload")
    return payload


def write_sanitized_snapshot(snapshot: dict[str, Any]) -> Path:
    settings = get_settings()
    output_dir = settings.dashboard_sanitized_dir / "codex"
    output_dir = resolve_repo_path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    snapshot_path = output_dir / "latest.json"
    snapshot_path.write_text(
        json.dumps(snapshot, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return snapshot_path


def _record_failure(started_at: str, safe_message: str) -> dict[str, Any]:
    finished_at = utc_now_iso()
    record_collector_run(
        collector_name=COLLECTOR_NAME,
        started_at=started_at,
        finished_at=finished_at,
        status="failed",
        safe_message=safe_message,
        records_written=0,
    )
    return {
        "status": "failed",
        "records_written": 0,
        "safe_message": safe_message,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Codex live usage collector")
    parser.parse_args()
    result = collect_codex_live_usage()
    printable = {
        "status": result["status"],
        "records_written": result["records_written"],
    }
    if "snapshot_file" in result:
        printable["snapshot_file"] = result["snapshot_file"]
    if "safe_message" in result:
        printable["safe_message"] = result["safe_message"]
    print(json.dumps(printable, sort_keys=True))


if __name__ == "__main__":
    main()
