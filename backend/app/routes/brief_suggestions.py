import sqlite3

from fastapi import APIRouter, HTTPException

from backend.app.db import (
    create_top_item,
    get_brief_suggestion,
    get_top_item,
    init_db,
    list_brief_suggestions,
    update_brief_suggestion,
    utc_now_iso,
)
from backend.app.models import (
    BriefSuggestion,
    BriefSuggestionsImportResponse,
    BriefSuggestionsResponse,
    TopItem,
)
from backend.app.routes.serializers import brief_suggestion_from_row, top_item_from_row
from backend.app.services.woodcraft_brief import (
    BriefImportError,
    import_woodcraft_brief_suggestions,
)
from backend.app.settings import get_settings

router = APIRouter(prefix="/api/brief-suggestions", tags=["brief-suggestions"])


@router.get("", response_model=BriefSuggestionsResponse)
def brief_suggestions() -> BriefSuggestionsResponse:
    init_db()
    return BriefSuggestionsResponse(
        suggestions=[
            brief_suggestion_from_row(row)
            for row in list_brief_suggestions(statuses=("pending",))
        ]
    )


@router.post("/import", response_model=BriefSuggestionsImportResponse)
def import_brief_suggestions() -> BriefSuggestionsImportResponse:
    init_db()
    try:
        result = import_woodcraft_brief_suggestions(
            source_path=get_settings().woodcraft_brief_source
        )
    except BriefImportError as exc:
        safe_message = public_import_safe_message(exc.safe_message)
        return BriefSuggestionsImportResponse(
            status="failed",
            imported=0,
            already_imported=0,
            skipped=0,
            safe_message=safe_message,
            message=public_import_user_message(safe_message),
        )

    return BriefSuggestionsImportResponse(
        status="success",
        imported=int(result["imported"]),
        already_imported=int(result["already_imported"]),
        skipped=int(result["skipped"]),
        safe_message="brief_suggestions_imported",
        message="Brief suggestions refreshed.",
    )


@router.post("/{suggestion_id}/accept", response_model=TopItem)
def accept_brief_suggestion(suggestion_id: int) -> TopItem:
    init_db()
    suggestion = get_brief_suggestion(suggestion_id)
    if suggestion is None:
        raise HTTPException(status_code=404, detail="brief_suggestion_not_found")
    if suggestion["status"] == "accepted":
        accepted_id = suggestion.get("accepted_top_item_id")
        if accepted_id:
            existing = get_top_item(int(accepted_id))
            if existing is not None:
                return top_item_from_row(existing)
        raise HTTPException(status_code=409, detail="brief_suggestion_already_accepted")
    if suggestion["status"] == "ignored":
        raise HTTPException(status_code=409, detail="brief_suggestion_ignored")

    try:
        top_item = create_top_item(
            {
                "title": suggestion["title"],
                "project_key": suggestion.get("project_key"),
                "reason": suggestion.get("reason"),
                "status": "pending",
                "pinned": False,
            }
        )
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail="brief_suggestion_not_accepted") from exc

    update_brief_suggestion(
        suggestion_id,
        {
            "status": "accepted",
            "accepted_top_item_id": top_item["id"],
            "accepted_at": utc_now_iso(),
            "ignored_at": None,
        },
    )
    return top_item_from_row(top_item)


@router.post("/{suggestion_id}/ignore", response_model=BriefSuggestion)
def ignore_brief_suggestion(suggestion_id: int) -> BriefSuggestion:
    init_db()
    suggestion = get_brief_suggestion(suggestion_id)
    if suggestion is None:
        raise HTTPException(status_code=404, detail="brief_suggestion_not_found")
    if suggestion["status"] == "accepted":
        raise HTTPException(status_code=409, detail="brief_suggestion_already_accepted")
    row = update_brief_suggestion(
        suggestion_id,
        {
            "status": "ignored",
            "ignored_at": utc_now_iso(),
        },
    )
    if row is None:
        raise HTTPException(status_code=404, detail="brief_suggestion_not_found")
    return brief_suggestion_from_row(row)


def public_import_safe_message(value: object) -> str:
    if value == "brief_source_not_available":
        return "brief_source_not_available"
    if value == "brief_source_invalid":
        return "brief_source_invalid"
    if value == "brief_source_unreadable":
        return "brief_source_unreadable"
    return "brief_suggestions_import_failed"


def public_import_user_message(safe_message: str) -> str:
    if safe_message == "brief_source_not_available":
        return "Brief suggestions could not be refreshed. Check local Brief Me export."
    if safe_message == "brief_source_invalid":
        return "Brief suggestions could not be refreshed. Brief Me export was not valid."
    return "Brief suggestions could not be refreshed. Try again later."
