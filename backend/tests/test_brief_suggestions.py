from pathlib import Path
from types import SimpleNamespace

from backend.app.db import (
    get_project,
    init_db,
    list_brief_suggestions,
)
from backend.app.routes import brief_suggestions as route_module
from backend.app.routes.daily import daily_dashboard
from backend.app.services.woodcraft_brief import import_woodcraft_brief_suggestions
from backend.app.settings import Settings, get_settings

FIXTURE = Path("backend/tests/fixtures/woodcraft_brief_latest.json")


def use_temp_db(tmp_path, monkeypatch):
    db_path = tmp_path / "dashboard.db"
    monkeypatch.setenv("DASHBOARD_DB_PATH", str(db_path))
    get_settings.cache_clear()
    init_db(db_path)
    return db_path


def test_import_brief_suggestions_is_sanitized_and_idempotent(tmp_path, monkeypatch):
    use_temp_db(tmp_path, monkeypatch)

    first = import_woodcraft_brief_suggestions(source_path=FIXTURE)
    second = import_woodcraft_brief_suggestions(source_path=FIXTURE)
    suggestions = list_brief_suggestions(statuses=("pending",))

    assert first == {
        "status": "success",
        "imported": 3,
        "already_imported": 0,
        "skipped": 0,
        "safe_message": "brief_suggestions_imported",
    }
    assert second["imported"] == 0
    assert second["already_imported"] == 3
    assert len(suggestions) == 3
    assert suggestions[0]["source_label"] == "Woodcraft Brief Me"
    assert get_project("woodcraft")["project_label"] == "Woodcraft Workspace"

    serialized = str(suggestions).lower()
    forbidden_terms = [
        "access_token",
        "refresh_token",
        "authorization",
        "raw_payload",
        "prompt_preview",
        ".jsonl",
    ]
    assert all(term not in serialized for term in forbidden_terms)


def test_import_route_returns_safe_counts_and_daily_suggestions(tmp_path, monkeypatch):
    use_temp_db(tmp_path, monkeypatch)
    monkeypatch.setenv("WOODCRAFT_BRIEF_SOURCE", str(FIXTURE))
    get_settings.cache_clear()

    response = route_module.import_brief_suggestions().model_dump()
    daily = daily_dashboard().model_dump()

    assert response["status"] == "success"
    assert response["imported"] == 3
    assert response["already_imported"] == 0
    assert response["skipped"] == 0
    assert response["safe_message"] == "brief_suggestions_imported"
    assert len(daily["brief_suggestions"]) == 3


def test_brief_source_defaults_to_not_configured(tmp_path, monkeypatch):
    use_temp_db(tmp_path, monkeypatch)
    assert Settings(_env_file=None).woodcraft_brief_source is None
    monkeypatch.setattr(
        route_module,
        "get_settings",
        lambda: SimpleNamespace(woodcraft_brief_source=None),
    )

    response = route_module.import_brief_suggestions().model_dump()

    assert response == {
        "status": "failed",
        "imported": 0,
        "already_imported": 0,
        "skipped": 0,
        "safe_message": "brief_source_not_configured",
        "message": "Brief suggestions are not configured. Set the source in local settings.",
    }
    assert ":\\" not in str(response)


def test_import_route_rejects_invalid_source_without_exposing_path(tmp_path, monkeypatch):
    use_temp_db(tmp_path, monkeypatch)
    invalid_source = tmp_path / "invalid_brief.json"
    invalid_source.write_text('{"source":"unexpected"}', encoding="utf-8")
    monkeypatch.setenv("WOODCRAFT_BRIEF_SOURCE", str(invalid_source))
    get_settings.cache_clear()

    response = route_module.import_brief_suggestions().model_dump()

    assert response["status"] == "failed"
    assert response["safe_message"] == "brief_source_invalid"
    assert str(invalid_source) not in str(response)
    assert ":\\" not in str(response)


def test_accept_and_ignore_brief_suggestions(tmp_path, monkeypatch):
    use_temp_db(tmp_path, monkeypatch)
    import_woodcraft_brief_suggestions(source_path=FIXTURE)
    suggestions = route_module.brief_suggestions().model_dump()["suggestions"]

    accepted_result = route_module.accept_brief_suggestion(suggestions[0]["id"]).model_dump()
    accepted = accepted_result["item"]
    ignored = route_module.ignore_brief_suggestion(suggestions[1]["id"]).model_dump()
    remaining = route_module.brief_suggestions().model_dump()["suggestions"]

    assert accepted["title"] == suggestions[0]["title"]
    assert accepted["pinned"] is False
    assert accepted["status"] == "active"
    assert accepted_result["placement"] == "active"
    assert accepted["source_suggestion_key"]
    assert ignored["status"] == "ignored"
    assert suggestions[0]["id"] not in {item["id"] for item in remaining}
    assert suggestions[1]["id"] not in {item["id"] for item in remaining}


def test_import_route_failure_does_not_expose_source_path(tmp_path, monkeypatch):
    use_temp_db(tmp_path, monkeypatch)
    missing_source = tmp_path / "missing_brief.json"
    monkeypatch.setenv("WOODCRAFT_BRIEF_SOURCE", str(missing_source))
    get_settings.cache_clear()

    response = route_module.import_brief_suggestions().model_dump()

    assert response["status"] == "failed"
    assert response["safe_message"] == "brief_source_not_available"
    serialized = str(response)
    assert str(missing_source) not in serialized
    assert ":\\" not in serialized
