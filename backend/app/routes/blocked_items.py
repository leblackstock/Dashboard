import sqlite3

from fastapi import APIRouter, HTTPException

from backend.app.db import (
    create_blocked_item,
    get_blocked_item,
    get_project,
    init_db,
    list_blocked_items,
    update_blocked_item,
)
from backend.app.models import (
    BlockedItem,
    BlockedItemCreate,
    BlockedItemsResponse,
    BlockedItemUpdate,
)
from backend.app.routes.serializers import blocked_item_from_row

router = APIRouter(prefix="/api/blocked-items", tags=["blocked-items"])


def _ensure_project_exists(project_key: str | None) -> None:
    if project_key and get_project(project_key) is None:
        raise HTTPException(status_code=400, detail="project_not_found")


@router.get("", response_model=BlockedItemsResponse)
def blocked_items(include_resolved: bool = False) -> BlockedItemsResponse:
    init_db()
    rows = list_blocked_items(include_resolved=include_resolved)
    return BlockedItemsResponse(items=[blocked_item_from_row(row) for row in rows])


@router.post("", response_model=BlockedItem)
def create_blocked_item_endpoint(payload: BlockedItemCreate) -> BlockedItem:
    init_db()
    item = payload.model_dump()
    _ensure_project_exists(item.get("project_key"))
    try:
        row = create_blocked_item(item)
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail="blocked_item_not_created") from exc
    return blocked_item_from_row(row)


@router.patch("/{item_id}", response_model=BlockedItem)
def update_blocked_item_endpoint(item_id: int, payload: BlockedItemUpdate) -> BlockedItem:
    init_db()
    if get_blocked_item(item_id) is None:
        raise HTTPException(status_code=404, detail="blocked_item_not_found")
    updates = payload.model_dump(exclude_unset=True)
    _ensure_project_exists(updates.get("project_key"))
    try:
        row = update_blocked_item(item_id, updates)
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail="blocked_item_not_updated") from exc
    if row is None:
        raise HTTPException(status_code=404, detail="blocked_item_not_found")
    return blocked_item_from_row(row)
