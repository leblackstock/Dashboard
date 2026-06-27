import sqlite3

from fastapi import APIRouter, HTTPException

from backend.app.db import (
    create_project,
    get_project,
    init_db,
    list_projects,
    update_project,
)
from backend.app.models import (
    Project,
    ProjectCreate,
    ProjectsResponse,
    ProjectStatus,
    ProjectUpdate,
)
from backend.app.routes.serializers import project_from_row, safe_project_key

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=ProjectsResponse)
def projects(status: ProjectStatus | None = None) -> ProjectsResponse:
    init_db()
    statuses = (status,) if status else None
    return ProjectsResponse(
        projects=[project_from_row(row) for row in list_projects(statuses=statuses)]
    )


@router.post("", response_model=Project)
def create_project_endpoint(payload: ProjectCreate) -> Project:
    init_db()
    project = payload.model_dump()
    project["project_key"] = project["project_key"] or safe_project_key(project["project_label"])
    try:
        row = create_project(project)
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail="project_not_created") from exc
    return project_from_row(row)


@router.patch("/{project_key}", response_model=Project)
def update_project_endpoint(project_key: str, payload: ProjectUpdate) -> Project:
    init_db()
    if get_project(project_key) is None:
        raise HTTPException(status_code=404, detail="project_not_found")
    try:
        row = update_project(project_key, payload.model_dump(exclude_unset=True))
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail="project_not_updated") from exc
    if row is None:
        raise HTTPException(status_code=404, detail="project_not_found")
    return project_from_row(row)
