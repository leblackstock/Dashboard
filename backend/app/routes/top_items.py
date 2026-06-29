import sqlite3

from fastapi import APIRouter, HTTPException

from backend.app.db import (
    get_project,
    get_top_item,
    init_db,
    list_top_items_for_daily,
    update_top_item,
)
from backend.app.models import (
    TopItem,
    TopItemCreate,
    TopItemPlacementResponse,
    TopItemReorderRequest,
    TopItemsResponse,
    TopItemUpdate,
)
from backend.app.routes.serializers import today_prefix, top_item_from_row
from backend.app.services.top_items import (
    TopItemWorkflowError,
    complete_priority,
    create_priority,
    promote_priority,
    remove_priority,
    reorder_active_priorities,
    return_priority_to_suggestions,
)

router = APIRouter(prefix="/api/top-items", tags=["top-items"])


def _ensure_project_exists(project_key: str | None) -> None:
    if project_key and get_project(project_key) is None:
        raise HTTPException(status_code=400, detail="project_not_found")


@router.get("", response_model=TopItemsResponse)
def top_items() -> TopItemsResponse:
    init_db()
    rows = list_top_items_for_daily(today=today_prefix())
    return TopItemsResponse(items=[top_item_from_row(row) for row in rows])


@router.post("", response_model=TopItemPlacementResponse)
def create_top_item_endpoint(payload: TopItemCreate) -> TopItemPlacementResponse:
    init_db()
    item = payload.model_dump()
    _ensure_project_exists(item.get("project_key"))
    try:
        row, placement = create_priority(item)
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail="top_item_not_created") from exc
    return placement_response(row, placement)


@router.put("/reorder", response_model=TopItemsResponse)
def reorder_top_items_endpoint(payload: TopItemReorderRequest) -> TopItemsResponse:
    init_db()
    try:
        rows = reorder_active_priorities(payload.item_ids)
    except TopItemWorkflowError as exc:
        raise_workflow_error(exc)
    return TopItemsResponse(items=[top_item_from_row(row) for row in rows])


@router.patch("/{item_id}", response_model=TopItem)
def update_top_item_endpoint(item_id: int, payload: TopItemUpdate) -> TopItem:
    init_db()
    if get_top_item(item_id) is None:
        raise HTTPException(status_code=404, detail="top_item_not_found")
    updates = payload.model_dump(exclude_unset=True)
    _ensure_project_exists(updates.get("project_key"))
    should_complete = updates.pop("status", None) == "completed"
    try:
        row = update_top_item(item_id, updates)
        if should_complete:
            row = complete_priority(item_id)
    except TopItemWorkflowError as exc:
        raise_workflow_error(exc)
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail="top_item_not_updated") from exc
    if row is None:
        raise HTTPException(status_code=404, detail="top_item_not_found")
    return top_item_from_row(row)


@router.post("/{item_id}/promote", response_model=TopItemPlacementResponse)
def promote_top_item_endpoint(item_id: int) -> TopItemPlacementResponse:
    init_db()
    try:
        row = promote_priority(item_id)
    except TopItemWorkflowError as exc:
        raise_workflow_error(exc)
    return TopItemPlacementResponse(
        item=top_item_from_row(row),
        placement="active",
        safe_message="top_item_promoted",
        message="Promoted to Top 3.",
    )


@router.post("/{item_id}/remove", response_model=TopItem)
def remove_top_item_endpoint(item_id: int) -> TopItem:
    init_db()
    try:
        row = remove_priority(item_id)
    except TopItemWorkflowError as exc:
        raise_workflow_error(exc)
    return top_item_from_row(row)


@router.post("/{item_id}/return-to-suggestions", response_model=TopItem)
def return_top_item_to_suggestions_endpoint(item_id: int) -> TopItem:
    init_db()
    try:
        row = return_priority_to_suggestions(item_id)
    except TopItemWorkflowError as exc:
        raise_workflow_error(exc)
    return top_item_from_row(row)


def placement_response(row: dict, placement: str) -> TopItemPlacementResponse:
    if placement == "queued":
        return TopItemPlacementResponse(
            item=top_item_from_row(row),
            placement="queued",
            safe_message="top_item_queued",
            message="Top 3 is full. Added to Priority Queue.",
        )
    return TopItemPlacementResponse(
        item=top_item_from_row(row),
        placement="active",
        safe_message="top_item_added",
        message="Added to Top 3.",
    )


def raise_workflow_error(exc: TopItemWorkflowError) -> None:
    status_code = (
        404
        if exc.safe_code in {"top_item_not_found", "brief_suggestion_not_found"}
        else 409
    )
    raise HTTPException(status_code=status_code, detail=exc.safe_code)
