import argparse
import sqlite3
from collections.abc import Iterable
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from backend.app.settings import get_settings

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "backend" / "db" / "schema.sql"


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def resolve_repo_path(path: Path) -> Path:
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def get_db_path(db_path: Path | None = None) -> Path:
    selected = db_path or get_settings().dashboard_db_path
    return resolve_repo_path(Path(selected))


@contextmanager
def connect(db_path: Path | None = None) -> Iterable[sqlite3.Connection]:
    resolved = get_db_path(db_path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(resolved)
    connection.row_factory = sqlite3.Row
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        yield connection
        connection.commit()
    finally:
        connection.close()


def init_db(db_path: Path | None = None) -> Path:
    resolved = get_db_path(db_path)
    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    with connect(resolved) as connection:
        connection.executescript(schema_sql)
    return resolved


def upsert_account(
    account: dict[str, Any],
    *,
    db_path: Path | None = None,
) -> None:
    now = utc_now_iso()
    with connect(db_path) as connection:
        connection.execute(
            """
            INSERT INTO ai_accounts (
              account_key_hash, provider, account_label, account_name,
              auth_mode, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(account_key_hash) DO UPDATE SET
              provider = excluded.provider,
              account_label = excluded.account_label,
              account_name = excluded.account_name,
              auth_mode = excluded.auth_mode,
              updated_at = excluded.updated_at
            """,
            (
                account["account_key_hash"],
                account.get("provider", "openai"),
                account.get("account_label"),
                account.get("account_name"),
                account.get("auth_mode", "codex_auth"),
                now,
                now,
            ),
        )


def insert_usage_snapshot(
    snapshot: dict[str, Any],
    *,
    db_path: Path | None = None,
) -> int:
    now = utc_now_iso()
    with connect(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO ai_usage_snapshots (
              provider, tool, account_key_hash, plan_type, reset_credits_available,
              quota_5h_used_percent, quota_5h_remaining_percent, quota_5h_reset_at,
              quota_weekly_used_percent, quota_weekly_remaining_percent, quota_weekly_reset_at,
              session_count, source_type, source_label, confidence,
              freshness, collected_at, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                snapshot["provider"],
                snapshot["tool"],
                snapshot["account_key_hash"],
                snapshot.get("plan_type"),
                snapshot.get("reset_credits_available"),
                snapshot.get("quota_5h_used_percent"),
                snapshot.get("quota_5h_remaining_percent"),
                snapshot.get("quota_5h_reset_at"),
                snapshot.get("quota_weekly_used_percent"),
                snapshot.get("quota_weekly_remaining_percent"),
                snapshot.get("quota_weekly_reset_at"),
                snapshot.get("session_count", 1),
                snapshot["source_type"],
                snapshot["source_label"],
                snapshot["confidence"],
                snapshot["freshness"],
                snapshot["collected_at"],
                now,
            ),
        )
        return int(cursor.lastrowid)


def record_collector_run(
    *,
    collector_name: str,
    started_at: str,
    finished_at: str,
    status: str,
    safe_message: str,
    records_written: int,
    db_path: Path | None = None,
) -> int:
    with connect(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO collector_runs (
              collector_name, started_at, finished_at, status, safe_message, records_written
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                collector_name,
                started_at,
                finished_at,
                status,
                safe_message,
                records_written,
            ),
        )
        return int(cursor.lastrowid)


def latest_codex_usage_rows(db_path: Path | None = None) -> list[sqlite3.Row]:
    with connect(db_path) as connection:
        rows = connection.execute(
            """
            SELECT
              s.*,
              a.account_label,
              a.account_name
            FROM ai_usage_snapshots AS s
            LEFT JOIN ai_accounts AS a
              ON a.account_key_hash = s.account_key_hash
            INNER JOIN (
              SELECT account_key_hash, MAX(id) AS latest_id
              FROM ai_usage_snapshots
              WHERE provider = 'openai' AND tool = 'codex'
              GROUP BY account_key_hash
            ) AS latest
              ON latest.latest_id = s.id
            ORDER BY s.collected_at DESC, s.id DESC
            """
        ).fetchall()
    return list(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Dashboard database helper")
    parser.add_argument("--init", action="store_true", help="Initialize the SQLite schema")
    args = parser.parse_args()

    if args.init:
        init_db()
        print("database_initialized=true")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
