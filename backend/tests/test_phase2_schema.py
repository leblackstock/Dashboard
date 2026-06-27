from backend.app.db import init_db, list_projects


def test_phase2_schema_is_idempotent_and_seeds_projects(tmp_path):
    db_path = tmp_path / "dashboard.db"

    init_db(db_path)
    init_db(db_path)

    projects = list_projects(db_path=db_path)
    project_keys = {project["project_key"] for project in projects}

    assert len(projects) == 10
    assert "dashboard-lifeops-command-center" in project_keys
    assert "other-unsorted" in project_keys
