from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class QuotaWindow(BaseModel):
    used_percent: float | None = None
    remaining_percent: float | None = None
    reset_at: str | None = None


class CodexUsageAccount(BaseModel):
    account_key_hash: str
    account_label: str | None = None
    account_name: str | None = None
    plan_type: str | None = None
    reset_credits_available: int | None = None
    quota_5h: QuotaWindow
    quota_weekly: QuotaWindow
    freshness: str
    confidence: str
    collected_at: str


class CodexUsageResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    accounts: list[CodexUsageAccount]


class CodexCollectResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["success", "failed"]
    records_written: int
    collected_at: str | None = None
    last_updated: str | None = None
    safe_message: str
    message: str


ProjectStatus = Literal["Active", "Paused", "Someday", "Archived", "Blocked", "Needs Review"]
TopItemStatus = Literal["pending", "in_progress", "completed"]
BriefSuggestionStatus = Literal["pending", "accepted", "ignored"]
BriefSuggestionSourceItemType = Literal["priority", "next_action"]
BlockedItemStatus = Literal["Blocked", "Needs Review", "Resolved"]


class ProjectCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_key: str | None = Field(default=None, max_length=80)
    project_label: str = Field(min_length=1, max_length=160)
    parent_project_key: str | None = Field(default=None, max_length=80)
    status: ProjectStatus = "Active"
    priority: int = 0
    default_ai_tool: str | None = Field(default=None, max_length=80)
    safe_notes: str | None = Field(default=None, max_length=1000)


class ProjectUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_label: str | None = Field(default=None, min_length=1, max_length=160)
    parent_project_key: str | None = Field(default=None, max_length=80)
    status: ProjectStatus | None = None
    priority: int | None = None
    default_ai_tool: str | None = Field(default=None, max_length=80)
    safe_notes: str | None = Field(default=None, max_length=1000)


class Project(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_key: str
    project_label: str
    parent_project_key: str | None
    status: ProjectStatus
    priority: int
    default_ai_tool: str | None
    safe_notes: str | None
    created_at: str
    updated_at: str


class ProjectsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    projects: list[Project]


class TopItemCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    project_key: str | None = Field(default=None, max_length=80)
    reason: str | None = Field(default=None, max_length=500)
    status: TopItemStatus = "pending"
    sort_order: int = 0
    pinned: bool = False


class TopItemUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=200)
    project_key: str | None = Field(default=None, max_length=80)
    reason: str | None = Field(default=None, max_length=500)
    status: TopItemStatus | None = None
    sort_order: int | None = None
    pinned: bool | None = None


class TopItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    title: str
    project_key: str | None
    project_label: str | None = None
    reason: str | None
    status: TopItemStatus
    sort_order: int
    pinned: bool
    display_state: Literal["normal", "completed_today"]
    created_at: str
    updated_at: str
    completed_at: str | None


class TopItemsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[TopItem]


class BriefSuggestion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    source: Literal["woodcraft_brief_me"]
    source_label: str
    briefing_date: str
    source_item_type: BriefSuggestionSourceItemType
    title: str
    reason: str | None
    project_key: str | None
    project_label: str | None = None
    urgency: str | None
    source_status: str | None
    status: BriefSuggestionStatus
    imported_at: str
    updated_at: str
    accepted_at: str | None
    ignored_at: str | None


class BriefSuggestionsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    suggestions: list[BriefSuggestion]


class BriefSuggestionsImportResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["success", "failed"]
    imported: int
    already_imported: int
    skipped: int
    safe_message: str
    message: str


class QuickCaptureCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1, max_length=2000)
    project_key: str | None = Field(default=None, max_length=80)
    capture_type: str | None = Field(default="note", max_length=40)
    status: str | None = Field(default="new", max_length=40)
    processed: bool = False


class QuickCaptureUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str | None = Field(default=None, min_length=1, max_length=2000)
    project_key: str | None = Field(default=None, max_length=80)
    capture_type: str | None = Field(default=None, max_length=40)
    status: str | None = Field(default=None, max_length=40)
    processed: bool | None = None


class QuickCapture(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    text: str
    captured_at: str
    project_key: str | None
    project_label: str | None = None
    capture_type: str | None
    status: str | None
    processed: bool
    created_at: str
    updated_at: str


class QuickCapturesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    captures: list[QuickCapture]


class BlockedItemCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_key: str | None = Field(default=None, max_length=80)
    title: str = Field(min_length=1, max_length=200)
    reason: str | None = Field(default=None, max_length=500)
    status: BlockedItemStatus = "Blocked"
    next_action: str | None = Field(default=None, max_length=500)


class BlockedItemUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_key: str | None = Field(default=None, max_length=80)
    title: str | None = Field(default=None, min_length=1, max_length=200)
    reason: str | None = Field(default=None, max_length=500)
    status: BlockedItemStatus | None = None
    next_action: str | None = Field(default=None, max_length=500)


class BlockedItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    project_key: str | None
    project_label: str | None = None
    title: str
    reason: str | None
    status: BlockedItemStatus
    next_action: str | None
    created_at: str
    updated_at: str
    resolved_at: str | None


class BlockedItemsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[BlockedItem]


class CollectorHealthItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    collector_name: str
    label: str
    latest_status: str
    last_success_at: str | None
    last_failed_at: str | None
    records_written: int
    safe_message: str
    freshness: str


class CollectorHealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    collectors: list[CollectorHealthItem]


class DailyDashboardResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    projects: list[Project]
    top_items: list[TopItem]
    brief_suggestions: list[BriefSuggestion]
    blocked_items: list[BlockedItem]
    quick_captures: list[QuickCapture]
    collector_health: list[CollectorHealthItem]
