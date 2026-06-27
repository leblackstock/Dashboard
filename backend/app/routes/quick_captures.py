import sqlite3

from fastapi import APIRouter, HTTPException, Query

from backend.app.db import (
    create_quick_capture,
    get_project,
    get_quick_capture,
    init_db,
    list_quick_captures,
    update_quick_capture,
)
from backend.app.models import (
    QuickCapture,
    QuickCaptureCreate,
    QuickCapturesResponse,
    QuickCaptureUpdate,
)
from backend.app.routes.serializers import quick_capture_from_row, validate_capture_text

router = APIRouter(prefix="/api/quick-captures", tags=["quick-captures"])


def _ensure_project_exists(project_key: str | None) -> None:
    if project_key and get_project(project_key) is None:
        raise HTTPException(status_code=400, detail="project_not_found")


@router.get("", response_model=QuickCapturesResponse)
def quick_captures(
    include_processed: bool = False,
    limit: int = Query(default=20, ge=1, le=100),
) -> QuickCapturesResponse:
    init_db()
    rows = list_quick_captures(limit=limit, include_processed=include_processed)
    return QuickCapturesResponse(captures=[quick_capture_from_row(row) for row in rows])


@router.post("", response_model=QuickCapture)
def create_quick_capture_endpoint(payload: QuickCaptureCreate) -> QuickCapture:
    init_db()
    capture = payload.model_dump()
    validate_capture_text(capture["text"])
    _ensure_project_exists(capture.get("project_key"))
    try:
        row = create_quick_capture(capture)
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail="quick_capture_not_created") from exc
    return quick_capture_from_row(row)


@router.patch("/{capture_id}", response_model=QuickCapture)
def update_quick_capture_endpoint(
    capture_id: int,
    payload: QuickCaptureUpdate,
) -> QuickCapture:
    init_db()
    if get_quick_capture(capture_id) is None:
        raise HTTPException(status_code=404, detail="quick_capture_not_found")
    updates = payload.model_dump(exclude_unset=True)
    if "text" in updates:
        validate_capture_text(updates["text"])
    _ensure_project_exists(updates.get("project_key"))
    try:
        row = update_quick_capture(capture_id, updates)
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail="quick_capture_not_updated") from exc
    if row is None:
        raise HTTPException(status_code=404, detail="quick_capture_not_found")
    return quick_capture_from_row(row)
