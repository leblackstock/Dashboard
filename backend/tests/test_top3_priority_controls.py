import sqlite3
from pathlib import Path

import pytest
from fastapi import HTTPException

from backend.app.db import (
    connect,
    get_brief_suggestion,
    get_top_item,
    init_db,
    list_top_items_for_daily,
)
from backend.app.models import TopItemCreate, TopItemReorderRequest, TopItemUpdate
from backend.app.routes import brief_suggestions as brief_routes
from backend.app.routes.daily import daily_dashboard
from backend.app.routes.top_items import (
    create_top_item_endpoint,
    promote_top_item_endpoint,
    remove_top_item_endpoint,
    reorder_top_items_endpoint,
    return_top_item_to_suggestions_endpoint,
    update_top_item_endpoint,
)
from backend.app.services.woodcraft_brief import import_woodcraft_brief_suggestions
from backend.app.settings import get_settings

FIXTURE = Path("backend/tests/fixtures/woodcraft_brief_latest.json")


def use_temp_db(tmp_path, monkeypatch):
    db_path = tmp_path / "dashboard.db"
    monkeypatch.setenv("DASHBOARD_DB_PATH", str(db_path))
    get_settings.cache_clear()
    init_db(db_path)
    return db_path


def add_manual(title: str):
    return create_top_item_endpoint(TopItemCreate(title=title)).model_dump()


def test_manual_add_routes_overflow_to_queue(tmp_path, monkeypatch):
    use_temp_db(tmp_path, monkeypatch)

    first = add_manual("Priority one")
    add_manual("Priority two")
    add_manual("Priority three")
    overflow = add_manual("Priority four")

    assert first["placement"] == "active"
    assert overflow["placement"] == "queued"
    assert overflow["safe_message"] == "top_item_queued"
    assert overflow["message"] == "Top 3 is full. Added to Priority Queue."


def test_active_limit_is_enforced_by_database(tmp_path, monkeypatch):
    db_path = use_temp_db(tmp_path, monkeypatch)
    for index in range(3):
        add_manual(f"Priority {index}")

    with (
        pytest.raises(sqlite3.IntegrityError, match="daily_top_items_active_limit"),
        connect(db_path) as connection,
    ):
        connection.execute(
            """
            INSERT INTO daily_top_items (
              title, status, sort_order, pinned, created_at, updated_at
            )
            VALUES ('Bypass attempt', 'active', 4, 0, '2026-06-29', '2026-06-29')
            """
        )


def test_brief_accept_routes_overflow_to_queue(tmp_path, monkeypatch):
    use_temp_db(tmp_path, monkeypatch)
    import_woodcraft_brief_suggestions(source_path=FIXTURE)
    suggestions = brief_routes.brief_suggestions().model_dump()["suggestions"]

    first = brief_routes.accept_brief_suggestion(suggestions[0]["id"]).model_dump()
    add_manual("Manual two")
    add_manual("Manual three")
    overflow = brief_routes.accept_brief_suggestion(suggestions[1]["id"]).model_dump()

    assert first["placement"] == "active"
    assert overflow["placement"] == "queued"
    assert overflow["item"]["source"] == "woodcraft_brief_me"
    assert overflow["item"]["source_item_type"] in {"priority", "next_action"}
    assert overflow["item"]["source_label"] == "Woodcraft Brief Me"

    reimported = import_woodcraft_brief_suggestions(source_path=FIXTURE)
    pending_ids = {
        item["id"] for item in brief_routes.brief_suggestions().model_dump()["suggestions"]
    }
    assert reimported["already_imported"] == 3
    assert suggestions[0]["id"] not in pending_ids
    assert suggestions[1]["id"] not in pending_ids


def test_reorder_and_manual_promotion_persist(tmp_path, monkeypatch):
    use_temp_db(tmp_path, monkeypatch)
    active = [add_manual(f"Active {index}")["item"] for index in range(3)]
    queued = add_manual("Queued")["item"]

    reordered = reorder_top_items_endpoint(
        TopItemReorderRequest(item_ids=[active[2]["id"], active[0]["id"], active[1]["id"]])
    ).model_dump()
    assert [item["id"] for item in reordered["items"]] == [
        active[2]["id"],
        active[0]["id"],
        active[1]["id"],
    ]

    with pytest.raises(HTTPException) as exc_info:
        promote_top_item_endpoint(queued["id"])
    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "top_3_full"

    remove_top_item_endpoint(active[0]["id"])
    promoted = promote_top_item_endpoint(queued["id"]).model_dump()
    assert promoted["item"]["status"] == "active"
    assert promoted["message"] == "Promoted to Top 3."


def test_remove_and_return_have_distinct_brief_behavior(tmp_path, monkeypatch):
    use_temp_db(tmp_path, monkeypatch)
    import_woodcraft_brief_suggestions(source_path=FIXTURE)
    suggestions = brief_routes.brief_suggestions().model_dump()["suggestions"]

    removed_result = brief_routes.accept_brief_suggestion(suggestions[0]["id"]).model_dump()
    removed_item = remove_top_item_endpoint(removed_result["item"]["id"]).model_dump()
    removed_suggestion = get_brief_suggestion(suggestions[0]["id"])

    assert removed_item["status"] == "removed"
    assert removed_item["completed_at"] is None
    assert removed_suggestion["status"] == "accepted"

    returned_result = brief_routes.accept_brief_suggestion(suggestions[1]["id"]).model_dump()
    returned_id = returned_result["item"]["id"]
    returned_item = return_top_item_to_suggestions_endpoint(returned_id).model_dump()
    returned_suggestion = get_brief_suggestion(suggestions[1]["id"])

    assert returned_item["status"] == "removed"
    assert returned_suggestion["status"] == "pending"
    assert returned_suggestion["accepted_top_item_id"] is None
    assert suggestions[1]["id"] in {
        item["id"] for item in brief_routes.brief_suggestions().model_dump()["suggestions"]
    }

    reaccepted = brief_routes.accept_brief_suggestion(suggestions[1]["id"]).model_dump()
    assert reaccepted["item"]["id"] == returned_id
    assert reaccepted["item"]["status"] == "active"


def test_handled_brief_items_do_not_reappear_on_import(tmp_path, monkeypatch):
    use_temp_db(tmp_path, monkeypatch)
    import_woodcraft_brief_suggestions(source_path=FIXTURE)
    suggestions = brief_routes.brief_suggestions().model_dump()["suggestions"]

    accepted = brief_routes.accept_brief_suggestion(suggestions[0]["id"]).model_dump()["item"]
    update_top_item_endpoint(accepted["id"], TopItemUpdate(status="completed"))
    brief_routes.ignore_brief_suggestion(suggestions[1]["id"])
    removed = brief_routes.accept_brief_suggestion(suggestions[2]["id"]).model_dump()["item"]
    remove_top_item_endpoint(removed["id"])

    result = import_woodcraft_brief_suggestions(source_path=FIXTURE)
    pending_ids = {
        item["id"] for item in brief_routes.brief_suggestions().model_dump()["suggestions"]
    }

    assert result["imported"] == 0
    assert result["already_imported"] == 3
    assert not pending_ids


def test_daily_response_hides_removed_and_stays_sanitized(tmp_path, monkeypatch):
    use_temp_db(tmp_path, monkeypatch)
    active = add_manual("Visible")["item"]
    removed = add_manual("Hidden")["item"]
    remove_top_item_endpoint(removed["id"])

    response = daily_dashboard().model_dump()
    ids = {item["id"] for item in response["top_items"]}
    serialized = str(response).lower()

    assert active["id"] in ids
    assert removed["id"] not in ids
    assert "brief_latest.json" not in serialized
    assert "authorization" not in serialized
    assert "access_token" not in serialized


def test_phase_2_7_migration_preserves_visible_order_and_backfills_source(
    tmp_path, monkeypatch
):
    db_path = tmp_path / "legacy.db"
    connection = sqlite3.connect(db_path)
    connection.executescript(
        """
        CREATE TABLE projects (
          project_key TEXT PRIMARY KEY,
          project_label TEXT NOT NULL,
          parent_project_key TEXT,
          status TEXT NOT NULL,
          priority INTEGER NOT NULL DEFAULT 0,
          default_ai_tool TEXT,
          safe_notes TEXT,
          created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL
        );
        INSERT INTO projects VALUES (
          'woodcraft', 'Woodcraft Workspace', NULL, 'Active', 0, NULL, NULL,
          '2026-06-27T00:00:00+00:00', '2026-06-27T00:00:00+00:00'
        );
        CREATE TABLE daily_top_items (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          title TEXT NOT NULL,
          project_key TEXT,
          reason TEXT,
          status TEXT NOT NULL DEFAULT 'pending'
            CHECK (status IN ('pending', 'in_progress', 'completed')),
          sort_order INTEGER NOT NULL DEFAULT 0,
          pinned INTEGER NOT NULL DEFAULT 0,
          created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL,
          completed_at TEXT
        );
        CREATE TABLE brief_suggestions (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          suggestion_key TEXT NOT NULL UNIQUE,
          source TEXT NOT NULL,
          source_label TEXT NOT NULL,
          briefing_date TEXT NOT NULL,
          source_item_type TEXT NOT NULL,
          source_item_index INTEGER NOT NULL,
          title TEXT NOT NULL,
          reason TEXT,
          project_key TEXT,
          urgency TEXT,
          source_status TEXT,
          status TEXT NOT NULL,
          accepted_top_item_id INTEGER,
          imported_at TEXT NOT NULL,
          updated_at TEXT NOT NULL,
          accepted_at TEXT,
          ignored_at TEXT
        );
        INSERT INTO daily_top_items (
          id, title, status, sort_order, pinned, created_at, updated_at
        ) VALUES
          (1, 'First', 'pending', 0, 0, '2026-06-27T01:00:00+00:00', '2026-06-27'),
          (2, 'Second', 'pending', 1, 0, '2026-06-27T02:00:00+00:00', '2026-06-27'),
          (3, 'Third', 'in_progress', 2, 0, '2026-06-27T03:00:00+00:00', '2026-06-27'),
          (4, 'Fourth', 'pending', 3, 0, '2026-06-27T04:00:00+00:00', '2026-06-27'),
          (5, 'Fifth', 'pending', 4, 0, '2026-06-27T05:00:00+00:00', '2026-06-27');
        INSERT INTO brief_suggestions (
          suggestion_key, source, source_label, briefing_date, source_item_type,
          source_item_index, title, project_key, status, accepted_top_item_id,
          imported_at, updated_at, accepted_at
        ) VALUES (
          'woodcraft_brief_me:safehash', 'woodcraft_brief_me', 'Woodcraft Brief Me',
          '2026-06-27', 'priority', 0, 'Second', 'woodcraft', 'accepted', 2,
          '2026-06-27', '2026-06-27', '2026-06-27'
        );
        """
    )
    connection.commit()
    connection.close()

    monkeypatch.setenv("DASHBOARD_DB_PATH", str(db_path))
    get_settings.cache_clear()
    init_db(db_path)

    items = list_top_items_for_daily(today="2026-06-29", db_path=db_path)
    assert [(item["title"], item["status"], item["sort_order"]) for item in items] == [
        ("First", "active", 0),
        ("Second", "active", 1),
        ("Third", "active", 2),
        ("Fourth", "queued", 0),
        ("Fifth", "queued", 1),
    ]
    second = get_top_item(2, db_path=db_path)
    assert second["source_suggestion_key"] == "woodcraft_brief_me:safehash"
    assert second["source_label"] == "Woodcraft Brief Me"
