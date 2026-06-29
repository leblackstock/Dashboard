from fastapi import APIRouter, HTTPException

from backend.app.db import (
    get_brief_suggestion,
    init_db,
    list_brief_suggestions,
    update_brief_suggestion,
    utc_now_iso,
)
from backend.app.models import (
    BriefSuggestion,
    BriefSuggestionsImportResponse,
    BriefSuggestionsResponse,
    TopItemPlacementResponse,
)
from backend.app.routes.serializers import brief_suggestion_from_row
from backend.app.routes.top_items import placement_response, raise_workflow_error
from backend.app.services.top_items import TopItemWorkflowError, accept_brief_priority
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
            duplicates_hidden=0,
            safe_message=safe_message,
            message=public_import_user_message(safe_message),
        )

    return BriefSuggestionsImportResponse(
        status="success",
        imported=int(result["imported"]),
        already_imported=int(result["already_imported"]),
        skipped=int(result["skipped"]),
        duplicates_hidden=int(result["duplicates_hidden"]),
        safe_message="brief_suggestions_imported",
        message="Brief suggestions refreshed.",
    )


@router.post("/{suggestion_id}/accept", response_model=TopItemPlacementResponse)
def accept_brief_suggestion(suggestion_id: int) -> TopItemPlacementResponse:
    init_db()
    try:
        top_item, placement = accept_brief_priority(suggestion_id)
    except TopItemWorkflowError as exc:
        raise_workflow_error(exc)
    return placement_response(top_item, placement)


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
    if value == "brief_source_not_configured":
        return "brief_source_not_configured"
    if value == "brief_source_not_available":
        return "brief_source_not_available"
    if value == "brief_source_invalid":
        return "brief_source_invalid"
    if value == "brief_source_unreadable":
        return "brief_source_unreadable"
    return "brief_suggestions_import_failed"


def public_import_user_message(safe_message: str) -> str:
    if safe_message == "brief_source_not_configured":
        return "Brief suggestions are not configured. Set the source in local settings."
    if safe_message == "brief_source_not_available":
        return "Brief suggestions could not be refreshed. Check local Brief Me export."
    if safe_message == "brief_source_invalid":
        return "Brief suggestions could not be refreshed. Brief Me export was not valid."
    return "Brief suggestions could not be refreshed. Try again later."
