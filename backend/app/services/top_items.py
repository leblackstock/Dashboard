from pathlib import Path
from typing import Any

from backend.app.db import connect, row_to_dict, utc_now_iso

ACTIVE_TOP_ITEM_LIMIT = 3


class TopItemWorkflowError(Exception):
    def __init__(self, safe_code: str) -> None:
        super().__init__(safe_code)
        self.safe_code = safe_code


def create_priority(
    item: dict[str, Any],
    *,
    db_path: Path | None = None,
) -> tuple[dict[str, Any], str]:
    with connect(db_path) as connection:
        connection.execute("BEGIN IMMEDIATE")
        placement = _available_placement(connection)
        item_id = _insert_top_item(
            connection,
            {
                **item,
                "status": placement,
                "sort_order": _next_sort_order(connection, placement),
            },
        )
        return _get_top_item(connection, item_id), placement


def accept_brief_priority(
    suggestion_id: int,
    *,
    db_path: Path | None = None,
) -> tuple[dict[str, Any], str]:
    with connect(db_path) as connection:
        connection.execute("BEGIN IMMEDIATE")
        suggestion = _get_brief_suggestion(connection, suggestion_id)
        if suggestion is None:
            raise TopItemWorkflowError("brief_suggestion_not_found")
        if suggestion["status"] == "ignored":
            raise TopItemWorkflowError("brief_suggestion_ignored")
        if suggestion["status"] == "accepted":
            accepted_id = suggestion.get("accepted_top_item_id")
            existing = _get_top_item(connection, int(accepted_id)) if accepted_id else None
            if existing and existing["status"] in {"active", "queued"}:
                return existing, str(existing["status"])
            raise TopItemWorkflowError("brief_suggestion_already_handled")

        placement = _available_placement(connection)
        sort_order = _next_sort_order(connection, placement)
        existing = connection.execute(
            "SELECT id, status FROM daily_top_items WHERE source_suggestion_key = ?",
            (suggestion["suggestion_key"],),
        ).fetchone()
        now = utc_now_iso()
        if existing is None:
            item_id = _insert_top_item(
                connection,
                {
                    "title": suggestion["title"],
                    "project_key": suggestion.get("project_key"),
                    "reason": suggestion.get("reason"),
                    "status": placement,
                    "sort_order": sort_order,
                    "source": suggestion["source"],
                    "source_suggestion_key": suggestion["suggestion_key"],
                    "source_item_type": suggestion["source_item_type"],
                    "source_label": suggestion["source_label"],
                },
            )
        else:
            if existing["status"] != "removed":
                raise TopItemWorkflowError("brief_suggestion_already_handled")
            item_id = int(existing["id"])
            connection.execute(
                """
                UPDATE daily_top_items
                SET
                  title = ?,
                  project_key = ?,
                  reason = ?,
                  status = ?,
                  sort_order = ?,
                  source = ?,
                  source_item_type = ?,
                  source_label = ?,
                  updated_at = ?,
                  completed_at = NULL
                WHERE id = ?
                """,
                (
                    suggestion["title"],
                    suggestion.get("project_key"),
                    suggestion.get("reason"),
                    placement,
                    sort_order,
                    suggestion["source"],
                    suggestion["source_item_type"],
                    suggestion["source_label"],
                    now,
                    item_id,
                ),
            )

        connection.execute(
            """
            UPDATE brief_suggestions
            SET
              status = 'accepted',
              accepted_top_item_id = ?,
              accepted_at = ?,
              ignored_at = NULL,
              updated_at = ?
            WHERE id = ?
            """,
            (item_id, now, now, suggestion_id),
        )
        return _get_top_item(connection, item_id), placement


def complete_priority(
    item_id: int,
    *,
    db_path: Path | None = None,
) -> dict[str, Any]:
    with connect(db_path) as connection:
        connection.execute("BEGIN IMMEDIATE")
        item = _require_open_top_item(connection, item_id)
        previous_status = str(item["status"])
        now = utc_now_iso()
        connection.execute(
            """
            UPDATE daily_top_items
            SET status = 'completed', completed_at = ?, updated_at = ?
            WHERE id = ?
            """,
            (now, now, item_id),
        )
        _normalize_sort_order(connection, previous_status)
        return _get_top_item(connection, item_id)


def promote_priority(
    item_id: int,
    *,
    db_path: Path | None = None,
) -> dict[str, Any]:
    with connect(db_path) as connection:
        connection.execute("BEGIN IMMEDIATE")
        item = _get_top_item(connection, item_id)
        if item is None:
            raise TopItemWorkflowError("top_item_not_found")
        if item["status"] != "queued":
            raise TopItemWorkflowError("top_item_not_queued")
        if _active_count(connection) >= ACTIVE_TOP_ITEM_LIMIT:
            raise TopItemWorkflowError("top_3_full")

        now = utc_now_iso()
        connection.execute(
            """
            UPDATE daily_top_items
            SET status = 'active', sort_order = ?, updated_at = ?
            WHERE id = ?
            """,
            (_next_sort_order(connection, "active"), now, item_id),
        )
        _normalize_sort_order(connection, "queued")
        return _get_top_item(connection, item_id)


def remove_priority(
    item_id: int,
    *,
    db_path: Path | None = None,
) -> dict[str, Any]:
    with connect(db_path) as connection:
        connection.execute("BEGIN IMMEDIATE")
        item = _require_open_top_item(connection, item_id)
        previous_status = str(item["status"])
        connection.execute(
            """
            UPDATE daily_top_items
            SET status = 'removed', completed_at = NULL, updated_at = ?
            WHERE id = ?
            """,
            (utc_now_iso(), item_id),
        )
        _normalize_sort_order(connection, previous_status)
        return _get_top_item(connection, item_id)


def return_priority_to_suggestions(
    item_id: int,
    *,
    db_path: Path | None = None,
) -> dict[str, Any]:
    with connect(db_path) as connection:
        connection.execute("BEGIN IMMEDIATE")
        item = _require_open_top_item(connection, item_id)
        suggestion_key = item.get("source_suggestion_key")
        if not suggestion_key:
            raise TopItemWorkflowError("top_item_not_brief_linked")

        suggestion = connection.execute(
            "SELECT * FROM brief_suggestions WHERE suggestion_key = ?",
            (suggestion_key,),
        ).fetchone()
        if (
            suggestion is None
            or suggestion["status"] != "accepted"
            or suggestion["accepted_top_item_id"] != item_id
        ):
            raise TopItemWorkflowError("brief_suggestion_link_not_available")

        previous_status = str(item["status"])
        now = utc_now_iso()
        connection.execute(
            """
            UPDATE daily_top_items
            SET status = 'removed', completed_at = NULL, updated_at = ?
            WHERE id = ?
            """,
            (now, item_id),
        )
        connection.execute(
            """
            UPDATE brief_suggestions
            SET
              status = 'pending',
              accepted_top_item_id = NULL,
              accepted_at = NULL,
              ignored_at = NULL,
              updated_at = ?
            WHERE id = ?
            """,
            (now, suggestion["id"]),
        )
        _normalize_sort_order(connection, previous_status)
        return _get_top_item(connection, item_id)


def reorder_active_priorities(
    item_ids: list[int],
    *,
    db_path: Path | None = None,
) -> list[dict[str, Any]]:
    if len(item_ids) != len(set(item_ids)):
        raise TopItemWorkflowError("top_item_order_invalid")

    with connect(db_path) as connection:
        connection.execute("BEGIN IMMEDIATE")
        current_ids = [
            int(row["id"])
            for row in connection.execute(
                """
                SELECT id
                FROM daily_top_items
                WHERE status = 'active'
                ORDER BY sort_order ASC, created_at ASC, id ASC
                """
            ).fetchall()
        ]
        if set(item_ids) != set(current_ids) or len(item_ids) != len(current_ids):
            raise TopItemWorkflowError("top_item_order_stale")

        now = utc_now_iso()
        for sort_order, item_id in enumerate(item_ids):
            connection.execute(
                "UPDATE daily_top_items SET sort_order = ?, updated_at = ? WHERE id = ?",
                (sort_order, now, item_id),
            )
        return [_get_top_item(connection, item_id) for item_id in item_ids]


def _available_placement(connection: Any) -> str:
    return "active" if _active_count(connection) < ACTIVE_TOP_ITEM_LIMIT else "queued"


def _active_count(connection: Any) -> int:
    row = connection.execute(
        "SELECT COUNT(*) AS count FROM daily_top_items WHERE status = 'active'"
    ).fetchone()
    return int(row["count"])


def _next_sort_order(connection: Any, status: str) -> int:
    row = connection.execute(
        """
        SELECT COALESCE(MAX(sort_order), -1) + 1 AS next_order
        FROM daily_top_items
        WHERE status = ?
        """,
        (status,),
    ).fetchone()
    return int(row["next_order"])


def _normalize_sort_order(connection: Any, status: str) -> None:
    rows = connection.execute(
        """
        SELECT id
        FROM daily_top_items
        WHERE status = ?
        ORDER BY sort_order ASC, created_at ASC, id ASC
        """,
        (status,),
    ).fetchall()
    for sort_order, row in enumerate(rows):
        connection.execute(
            "UPDATE daily_top_items SET sort_order = ? WHERE id = ?",
            (sort_order, row["id"]),
        )


def _require_open_top_item(connection: Any, item_id: int) -> dict[str, Any]:
    item = _get_top_item(connection, item_id)
    if item is None:
        raise TopItemWorkflowError("top_item_not_found")
    if item["status"] not in {"active", "queued"}:
        raise TopItemWorkflowError("top_item_not_open")
    return item


def _insert_top_item(connection: Any, item: dict[str, Any]) -> int:
    now = utc_now_iso()
    cursor = connection.execute(
        """
        INSERT INTO daily_top_items (
          title, project_key, reason, status, sort_order, pinned,
          source, source_suggestion_key, source_item_type, source_label,
          created_at, updated_at, completed_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)
        """,
        (
            item["title"],
            item.get("project_key"),
            item.get("reason"),
            item["status"],
            item["sort_order"],
            1 if item.get("pinned", False) else 0,
            item.get("source"),
            item.get("source_suggestion_key"),
            item.get("source_item_type"),
            item.get("source_label"),
            now,
            now,
        ),
    )
    return int(cursor.lastrowid)


def _get_top_item(connection: Any, item_id: int) -> dict[str, Any] | None:
    row = connection.execute(
        """
        SELECT t.*, p.project_label
        FROM daily_top_items AS t
        LEFT JOIN projects AS p
          ON p.project_key = t.project_key
        WHERE t.id = ?
        """,
        (item_id,),
    ).fetchone()
    return row_to_dict(row) if row else None


def _get_brief_suggestion(connection: Any, suggestion_id: int) -> dict[str, Any] | None:
    row = connection.execute(
        "SELECT * FROM brief_suggestions WHERE id = ?",
        (suggestion_id,),
    ).fetchone()
    return row_to_dict(row) if row else None
