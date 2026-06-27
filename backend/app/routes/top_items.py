import sqlite3

from fastapi import APIRouter, HTTPException

from backend.app.db import (
    create_top_item,
    get_project,
    get_top_item,
    init_db,
    list_top_items_for_daily,
    update_top_item,
)
from backend.app.models import TopItem, TopItemCreate, TopItemsResponse, TopItemUpdate
from backend.app.routes.serializers import today_prefix, top_item_from_row

router = APIRouter(prefix="/api/top-items", tags=["top-items"])


def _ensure_project_exists(project_key: str | None) -> None:
    if project_key and get_project(project_key) is None:
        raise HTTPException(status_code=400, detail="project_not_found")


@router.get("", response_model=TopItemsResponse)
def top_items() -> TopItemsResponse:
    init_db()
    rows = list_top_items_for_daily(today=today_prefix())
    return TopItemsResponse(items=[top_item_from_row(row) for row in rows])


@router.post("", response_model=TopItem)
def create_top_item_endpoint(payload: TopItemCreate) -> TopItem:
    init_db()
    item = payload.model_dump()
    _ensure_project_exists(item.get("project_key"))
    try:
        row = create_top_item(item)
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail="top_item_not_created") from exc
    return top_item_from_row(row)


@router.patch("/{item_id}", response_model=TopItem)
def update_top_item_endpoint(item_id: int, payload: TopItemUpdate) -> TopItem:
    init_db()
    if get_top_item(item_id) is None:
        raise HTTPException(status_code=404, detail="top_item_not_found")
    updates = payload.model_dump(exclude_unset=True)
    _ensure_project_exists(updates.get("project_key"))
    try:
        row = update_top_item(item_id, updates)
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail="top_item_not_updated") from exc
    if row is None:
        raise HTTPException(status_code=404, detail="top_item_not_found")
    return top_item_from_row(row)
