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


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return dict(row)


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
            WHERE
              s.provider = 'openai'
              AND s.tool = 'codex'
              AND s.id = (
                SELECT s2.id
                FROM ai_usage_snapshots AS s2
                WHERE
                  s2.provider = 'openai'
                  AND s2.tool = 'codex'
                  AND s2.account_key_hash = s.account_key_hash
                ORDER BY s2.collected_at DESC, s2.id DESC
                LIMIT 1
              )
            ORDER BY s.collected_at DESC, s.id DESC
            """
        ).fetchall()
    return list(rows)


def list_projects(
    *,
    statuses: tuple[str, ...] | None = None,
    db_path: Path | None = None,
) -> list[dict[str, Any]]:
    with connect(db_path) as connection:
        if statuses:
            placeholders = ", ".join("?" for _ in statuses)
            rows = connection.execute(
                f"""
                SELECT *
                FROM projects
                WHERE status IN ({placeholders})
                ORDER BY priority ASC, project_label ASC
                """,
                statuses,
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT *
                FROM projects
                ORDER BY priority ASC, project_label ASC
                """
            ).fetchall()
    return [row_to_dict(row) for row in rows]


def get_project(project_key: str, *, db_path: Path | None = None) -> dict[str, Any] | None:
    with connect(db_path) as connection:
        row = connection.execute(
            "SELECT * FROM projects WHERE project_key = ?",
            (project_key,),
        ).fetchone()
    return row_to_dict(row) if row else None


def create_project(project: dict[str, Any], *, db_path: Path | None = None) -> dict[str, Any]:
    now = utc_now_iso()
    with connect(db_path) as connection:
        connection.execute(
            """
            INSERT INTO projects (
              project_key, project_label, parent_project_key, status, priority,
              default_ai_tool, safe_notes, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                project["project_key"],
                project["project_label"],
                project.get("parent_project_key"),
                project.get("status", "Active"),
                project.get("priority", 0),
                project.get("default_ai_tool"),
                project.get("safe_notes"),
                now,
                now,
            ),
        )
    selected = get_project(project["project_key"], db_path=db_path)
    if selected is None:
        raise RuntimeError("project_create_failed")
    return selected


def ensure_project(
    *,
    project_key: str,
    project_label: str,
    priority: int = 0,
    default_ai_tool: str | None = None,
    safe_notes: str | None = None,
    db_path: Path | None = None,
) -> dict[str, Any]:
    selected = get_project(project_key, db_path=db_path)
    if selected is not None:
        return selected
    return create_project(
        {
            "project_key": project_key,
            "project_label": project_label,
            "priority": priority,
            "status": "Active",
            "default_ai_tool": default_ai_tool,
            "safe_notes": safe_notes,
        },
        db_path=db_path,
    )


def update_project(
    project_key: str,
    updates: dict[str, Any],
    *,
    db_path: Path | None = None,
) -> dict[str, Any] | None:
    allowed_fields = {
        "project_label",
        "parent_project_key",
        "status",
        "priority",
        "default_ai_tool",
        "safe_notes",
    }
    selected_updates = {key: value for key, value in updates.items() if key in allowed_fields}
    if not selected_updates:
        return get_project(project_key, db_path=db_path)

    selected_updates["updated_at"] = utc_now_iso()
    set_clause = ", ".join(f"{key} = ?" for key in selected_updates)
    values = [*selected_updates.values(), project_key]
    with connect(db_path) as connection:
        connection.execute(
            f"UPDATE projects SET {set_clause} WHERE project_key = ?",
            values,
        )
    return get_project(project_key, db_path=db_path)


def list_top_items_for_daily(
    *,
    today: str | None = None,
    db_path: Path | None = None,
) -> list[dict[str, Any]]:
    today = today or utc_now_iso().split("T", maxsplit=1)[0]
    with connect(db_path) as connection:
        rows = connection.execute(
            """
            SELECT
              t.*,
              p.project_label
            FROM daily_top_items AS t
            LEFT JOIN projects AS p
              ON p.project_key = t.project_key
            WHERE
              t.status != 'completed'
              OR (
                t.completed_at IS NOT NULL
                AND substr(t.completed_at, 1, 10) = ?
              )
            ORDER BY t.pinned DESC, t.sort_order ASC, t.created_at ASC, t.id ASC
            """,
            (today,),
        ).fetchall()
    return [row_to_dict(row) for row in rows]


def get_top_item(item_id: int, *, db_path: Path | None = None) -> dict[str, Any] | None:
    with connect(db_path) as connection:
        row = connection.execute(
            """
            SELECT
              t.*,
              p.project_label
            FROM daily_top_items AS t
            LEFT JOIN projects AS p
              ON p.project_key = t.project_key
            WHERE t.id = ?
            """,
            (item_id,),
        ).fetchone()
    return row_to_dict(row) if row else None


def create_top_item(item: dict[str, Any], *, db_path: Path | None = None) -> dict[str, Any]:
    now = utc_now_iso()
    completed_at = item.get("completed_at")
    if item.get("status") == "completed" and not completed_at:
        completed_at = now

    with connect(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO daily_top_items (
              title, project_key, reason, status, sort_order, pinned,
              created_at, updated_at, completed_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item["title"],
                item.get("project_key"),
                item.get("reason"),
                item.get("status", "pending"),
                item.get("sort_order", 0),
                1 if item.get("pinned", False) else 0,
                now,
                now,
                completed_at,
            ),
        )
        item_id = int(cursor.lastrowid)
    selected = get_top_item(item_id, db_path=db_path)
    if selected is None:
        raise RuntimeError("top_item_create_failed")
    return selected


def update_top_item(
    item_id: int,
    updates: dict[str, Any],
    *,
    db_path: Path | None = None,
) -> dict[str, Any] | None:
    allowed_fields = {
        "title",
        "project_key",
        "reason",
        "status",
        "sort_order",
        "pinned",
        "completed_at",
    }
    selected_updates = {key: value for key, value in updates.items() if key in allowed_fields}
    if not selected_updates:
        return get_top_item(item_id, db_path=db_path)

    if selected_updates.get("status") == "completed" and "completed_at" not in selected_updates:
        selected_updates["completed_at"] = utc_now_iso()
    if selected_updates.get("status") in {"pending", "in_progress"}:
        selected_updates["completed_at"] = None
    if "pinned" in selected_updates:
        selected_updates["pinned"] = 1 if selected_updates["pinned"] else 0

    selected_updates["updated_at"] = utc_now_iso()
    set_clause = ", ".join(f"{key} = ?" for key in selected_updates)
    values = [*selected_updates.values(), item_id]
    with connect(db_path) as connection:
        connection.execute(
            f"UPDATE daily_top_items SET {set_clause} WHERE id = ?",
            values,
        )
    return get_top_item(item_id, db_path=db_path)


def list_brief_suggestions(
    *,
    statuses: tuple[str, ...] = ("pending",),
    limit: int = 20,
    db_path: Path | None = None,
) -> list[dict[str, Any]]:
    limit = max(1, min(limit, 100))
    with connect(db_path) as connection:
        if statuses:
            placeholders = ", ".join("?" for _ in statuses)
            rows = connection.execute(
                f"""
                SELECT
                  s.*,
                  p.project_label
                FROM brief_suggestions AS s
                LEFT JOIN projects AS p
                  ON p.project_key = s.project_key
                WHERE s.status IN ({placeholders})
                ORDER BY s.imported_at DESC, s.id DESC
                LIMIT ?
                """,
                (*statuses, limit),
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT
                  s.*,
                  p.project_label
                FROM brief_suggestions AS s
                LEFT JOIN projects AS p
                  ON p.project_key = s.project_key
                ORDER BY s.imported_at DESC, s.id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
    return [row_to_dict(row) for row in rows]


def get_brief_suggestion(
    suggestion_id: int,
    *,
    db_path: Path | None = None,
) -> dict[str, Any] | None:
    with connect(db_path) as connection:
        row = connection.execute(
            """
            SELECT
              s.*,
              p.project_label
            FROM brief_suggestions AS s
            LEFT JOIN projects AS p
              ON p.project_key = s.project_key
            WHERE s.id = ?
            """,
            (suggestion_id,),
        ).fetchone()
    return row_to_dict(row) if row else None


def insert_brief_suggestion(
    suggestion: dict[str, Any],
    *,
    db_path: Path | None = None,
) -> bool:
    now = utc_now_iso()
    with connect(db_path) as connection:
        existing = connection.execute(
            "SELECT id FROM brief_suggestions WHERE suggestion_key = ?",
            (suggestion["suggestion_key"],),
        ).fetchone()
        if existing is not None:
            return False
        connection.execute(
            """
            INSERT INTO brief_suggestions (
              suggestion_key, source, source_label, briefing_date, source_item_type,
              source_item_index, title, reason, project_key, urgency, source_status, status,
              imported_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                suggestion["suggestion_key"],
                suggestion["source"],
                suggestion["source_label"],
                suggestion["briefing_date"],
                suggestion["source_item_type"],
                suggestion["source_item_index"],
                suggestion["title"],
                suggestion.get("reason"),
                suggestion.get("project_key"),
                suggestion.get("urgency"),
                suggestion.get("source_status"),
                suggestion.get("status", "pending"),
                now,
                now,
            ),
        )
    return True


def update_brief_suggestion(
    suggestion_id: int,
    updates: dict[str, Any],
    *,
    db_path: Path | None = None,
) -> dict[str, Any] | None:
    allowed_fields = {
        "status",
        "accepted_top_item_id",
        "accepted_at",
        "ignored_at",
    }
    selected_updates = {key: value for key, value in updates.items() if key in allowed_fields}
    if not selected_updates:
        return get_brief_suggestion(suggestion_id, db_path=db_path)

    selected_updates["updated_at"] = utc_now_iso()
    set_clause = ", ".join(f"{key} = ?" for key in selected_updates)
    values = [*selected_updates.values(), suggestion_id]
    with connect(db_path) as connection:
        connection.execute(
            f"UPDATE brief_suggestions SET {set_clause} WHERE id = ?",
            values,
        )
    return get_brief_suggestion(suggestion_id, db_path=db_path)


def list_quick_captures(
    *,
    limit: int = 20,
    include_processed: bool = False,
    db_path: Path | None = None,
) -> list[dict[str, Any]]:
    limit = max(1, min(limit, 100))
    with connect(db_path) as connection:
        if include_processed:
            rows = connection.execute(
                """
                SELECT
                  c.*,
                  p.project_label
                FROM quick_captures AS c
                LEFT JOIN projects AS p
                  ON p.project_key = c.project_key
                ORDER BY c.captured_at DESC, c.id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT
                  c.*,
                  p.project_label
                FROM quick_captures AS c
                LEFT JOIN projects AS p
                  ON p.project_key = c.project_key
                WHERE c.processed = 0
                ORDER BY c.captured_at DESC, c.id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
    return [row_to_dict(row) for row in rows]


def get_quick_capture(capture_id: int, *, db_path: Path | None = None) -> dict[str, Any] | None:
    with connect(db_path) as connection:
        row = connection.execute(
            """
            SELECT
              c.*,
              p.project_label
            FROM quick_captures AS c
            LEFT JOIN projects AS p
              ON p.project_key = c.project_key
            WHERE c.id = ?
            """,
            (capture_id,),
        ).fetchone()
    return row_to_dict(row) if row else None


def create_quick_capture(
    capture: dict[str, Any],
    *,
    db_path: Path | None = None,
) -> dict[str, Any]:
    now = utc_now_iso()
    captured_at = capture.get("captured_at") or now
    with connect(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO quick_captures (
              text, captured_at, project_key, capture_type, status, processed,
              created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                capture["text"],
                captured_at,
                capture.get("project_key"),
                capture.get("capture_type"),
                capture.get("status"),
                1 if capture.get("processed", False) else 0,
                now,
                now,
            ),
        )
        capture_id = int(cursor.lastrowid)
    selected = get_quick_capture(capture_id, db_path=db_path)
    if selected is None:
        raise RuntimeError("quick_capture_create_failed")
    return selected


def update_quick_capture(
    capture_id: int,
    updates: dict[str, Any],
    *,
    db_path: Path | None = None,
) -> dict[str, Any] | None:
    allowed_fields = {"text", "project_key", "capture_type", "status", "processed"}
    selected_updates = {key: value for key, value in updates.items() if key in allowed_fields}
    if not selected_updates:
        return get_quick_capture(capture_id, db_path=db_path)

    if "processed" in selected_updates:
        selected_updates["processed"] = 1 if selected_updates["processed"] else 0
    selected_updates["updated_at"] = utc_now_iso()
    set_clause = ", ".join(f"{key} = ?" for key in selected_updates)
    values = [*selected_updates.values(), capture_id]
    with connect(db_path) as connection:
        connection.execute(
            f"UPDATE quick_captures SET {set_clause} WHERE id = ?",
            values,
        )
    return get_quick_capture(capture_id, db_path=db_path)


def list_blocked_items(
    *,
    include_resolved: bool = False,
    db_path: Path | None = None,
) -> list[dict[str, Any]]:
    with connect(db_path) as connection:
        if include_resolved:
            rows = connection.execute(
                """
                SELECT
                  b.*,
                  p.project_label
                FROM blocked_items AS b
                LEFT JOIN projects AS p
                  ON p.project_key = b.project_key
                ORDER BY b.created_at DESC, b.id DESC
                """
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT
                  b.*,
                  p.project_label
                FROM blocked_items AS b
                LEFT JOIN projects AS p
                  ON p.project_key = b.project_key
                WHERE b.status != 'Resolved'
                ORDER BY b.created_at DESC, b.id DESC
                """
            ).fetchall()
    return [row_to_dict(row) for row in rows]


def get_blocked_item(item_id: int, *, db_path: Path | None = None) -> dict[str, Any] | None:
    with connect(db_path) as connection:
        row = connection.execute(
            """
            SELECT
              b.*,
              p.project_label
            FROM blocked_items AS b
            LEFT JOIN projects AS p
              ON p.project_key = b.project_key
            WHERE b.id = ?
            """,
            (item_id,),
        ).fetchone()
    return row_to_dict(row) if row else None


def create_blocked_item(item: dict[str, Any], *, db_path: Path | None = None) -> dict[str, Any]:
    now = utc_now_iso()
    resolved_at = item.get("resolved_at")
    if item.get("status") == "Resolved" and not resolved_at:
        resolved_at = now
    with connect(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO blocked_items (
              project_key, title, reason, status, next_action,
              created_at, updated_at, resolved_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item.get("project_key"),
                item["title"],
                item.get("reason"),
                item.get("status", "Blocked"),
                item.get("next_action"),
                now,
                now,
                resolved_at,
            ),
        )
        item_id = int(cursor.lastrowid)
    selected = get_blocked_item(item_id, db_path=db_path)
    if selected is None:
        raise RuntimeError("blocked_item_create_failed")
    return selected


def update_blocked_item(
    item_id: int,
    updates: dict[str, Any],
    *,
    db_path: Path | None = None,
) -> dict[str, Any] | None:
    allowed_fields = {"project_key", "title", "reason", "status", "next_action", "resolved_at"}
    selected_updates = {key: value for key, value in updates.items() if key in allowed_fields}
    if not selected_updates:
        return get_blocked_item(item_id, db_path=db_path)

    if selected_updates.get("status") == "Resolved" and "resolved_at" not in selected_updates:
        selected_updates["resolved_at"] = utc_now_iso()
    if selected_updates.get("status") in {"Blocked", "Needs Review"}:
        selected_updates["resolved_at"] = None
    selected_updates["updated_at"] = utc_now_iso()
    set_clause = ", ".join(f"{key} = ?" for key in selected_updates)
    values = [*selected_updates.values(), item_id]
    with connect(db_path) as connection:
        connection.execute(
            f"UPDATE blocked_items SET {set_clause} WHERE id = ?",
            values,
        )
    return get_blocked_item(item_id, db_path=db_path)


def latest_collector_run(
    collector_name: str,
    *,
    status: str | None = None,
    db_path: Path | None = None,
) -> dict[str, Any] | None:
    with connect(db_path) as connection:
        if status is None:
            row = connection.execute(
                """
                SELECT *
                FROM collector_runs
                WHERE collector_name = ?
                ORDER BY started_at DESC, id DESC
                LIMIT 1
                """,
                (collector_name,),
            ).fetchone()
        else:
            row = connection.execute(
                """
                SELECT *
                FROM collector_runs
                WHERE collector_name = ? AND status = ?
                ORDER BY started_at DESC, id DESC
                LIMIT 1
                """,
                (collector_name, status),
            ).fetchone()
    return row_to_dict(row) if row else None


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
