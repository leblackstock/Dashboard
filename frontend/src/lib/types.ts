export type QuotaWindow = {
  used_percent: number | null;
  remaining_percent: number | null;
  reset_at: string | null;
};

export type CodexUsageAccount = {
  account_key_hash: string;
  account_label: string | null;
  account_name: string | null;
  plan_type: string | null;
  reset_credits_available: number | null;
  quota_5h: QuotaWindow;
  quota_weekly: QuotaWindow;
  freshness: string;
  confidence: string;
  collected_at: string;
};

export type CodexUsageResponse = {
  accounts: CodexUsageAccount[];
};

export type CodexCollectResponse = {
  status: "success" | "failed";
  records_written: number;
  collected_at: string | null;
  last_updated: string | null;
  safe_message: string;
  message: string;
};

export type ProjectStatus =
  | "Active"
  | "Paused"
  | "Someday"
  | "Archived"
  | "Blocked"
  | "Needs Review";

export type Project = {
  project_key: string;
  project_label: string;
  parent_project_key: string | null;
  status: ProjectStatus;
  priority: number;
  default_ai_tool: string | null;
  safe_notes: string | null;
  created_at: string;
  updated_at: string;
};

export type TopItemStatus = "pending" | "in_progress" | "completed";

export type TopItem = {
  id: number;
  title: string;
  project_key: string | null;
  project_label: string | null;
  reason: string | null;
  status: TopItemStatus;
  sort_order: number;
  pinned: boolean;
  display_state: "normal" | "completed_today";
  created_at: string;
  updated_at: string;
  completed_at: string | null;
};

export type BriefSuggestion = {
  id: number;
  source: "woodcraft_brief_me";
  source_label: string;
  briefing_date: string;
  source_item_type: "priority" | "next_action";
  title: string;
  reason: string | null;
  project_key: string | null;
  project_label: string | null;
  urgency: string | null;
  source_status: string | null;
  status: "pending" | "accepted" | "ignored";
  imported_at: string;
  updated_at: string;
  accepted_at: string | null;
  ignored_at: string | null;
};

export type BriefSuggestionsImportResponse = {
  status: "success" | "failed";
  imported: number;
  already_imported: number;
  skipped: number;
  safe_message: string;
  message: string;
};

export type QuickCapture = {
  id: number;
  text: string;
  captured_at: string;
  project_key: string | null;
  project_label: string | null;
  capture_type: string | null;
  status: string | null;
  processed: boolean;
  created_at: string;
  updated_at: string;
};

export type BlockedItemStatus = "Blocked" | "Needs Review" | "Resolved";

export type BlockedItem = {
  id: number;
  project_key: string | null;
  project_label: string | null;
  title: string;
  reason: string | null;
  status: BlockedItemStatus;
  next_action: string | null;
  created_at: string;
  updated_at: string;
  resolved_at: string | null;
};

export type CollectorHealthItem = {
  collector_name: string;
  label: string;
  latest_status: string;
  last_success_at: string | null;
  last_failed_at: string | null;
  records_written: number;
  safe_message: string;
  freshness: string;
};

export type DailyDashboardResponse = {
  projects: Project[];
  top_items: TopItem[];
  brief_suggestions: BriefSuggestion[];
  blocked_items: BlockedItem[];
  quick_captures: QuickCapture[];
  collector_health: CollectorHealthItem[];
};

export type ProjectCreate = {
  project_label: string;
  status?: ProjectStatus;
  priority?: number;
  default_ai_tool?: string | null;
  safe_notes?: string | null;
};

export type TopItemCreate = {
  title: string;
  project_key?: string | null;
  reason?: string | null;
  status?: TopItemStatus;
};

export type TopItemUpdate = Partial<{
  title: string;
  project_key: string | null;
  reason: string | null;
  status: TopItemStatus;
  sort_order: number;
  pinned: boolean;
}>;

export type QuickCaptureCreate = {
  text: string;
  project_key?: string | null;
  capture_type?: string | null;
  status?: string | null;
};

export type BlockedItemCreate = {
  title: string;
  project_key?: string | null;
  reason?: string | null;
  status?: BlockedItemStatus;
  next_action?: string | null;
};

export type BlockedItemUpdate = Partial<{
  title: string;
  project_key: string | null;
  reason: string | null;
  status: BlockedItemStatus;
  next_action: string | null;
}>;
