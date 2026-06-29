PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS ai_accounts (
  account_key_hash TEXT PRIMARY KEY,
  provider TEXT NOT NULL,
  account_label TEXT,
  account_name TEXT,
  auth_mode TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ai_usage_snapshots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  provider TEXT NOT NULL,
  tool TEXT NOT NULL,
  account_key_hash TEXT NOT NULL,
  plan_type TEXT,
  reset_credits_available INTEGER,
  quota_5h_used_percent REAL,
  quota_5h_remaining_percent REAL,
  quota_5h_reset_at TEXT,
  quota_weekly_used_percent REAL,
  quota_weekly_remaining_percent REAL,
  quota_weekly_reset_at TEXT,
  session_count INTEGER NOT NULL DEFAULT 1,
  source_type TEXT NOT NULL,
  source_label TEXT NOT NULL,
  confidence TEXT NOT NULL,
  freshness TEXT NOT NULL,
  collected_at TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (account_key_hash) REFERENCES ai_accounts(account_key_hash)
);

CREATE INDEX IF NOT EXISTS idx_ai_usage_snapshots_provider_tool_account
  ON ai_usage_snapshots(provider, tool, account_key_hash, id DESC);

CREATE INDEX IF NOT EXISTS idx_ai_usage_snapshots_collected_at
  ON ai_usage_snapshots(collected_at DESC);

CREATE TABLE IF NOT EXISTS collector_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  collector_name TEXT NOT NULL,
  started_at TEXT NOT NULL,
  finished_at TEXT NOT NULL,
  status TEXT NOT NULL,
  safe_message TEXT NOT NULL,
  records_written INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_collector_runs_name_started
  ON collector_runs(collector_name, started_at DESC);

CREATE TABLE IF NOT EXISTS projects (
  project_key TEXT PRIMARY KEY,
  project_label TEXT NOT NULL,
  parent_project_key TEXT,
  status TEXT NOT NULL DEFAULT 'Active'
    CHECK (status IN ('Active', 'Paused', 'Someday', 'Archived', 'Blocked', 'Needs Review')),
  priority INTEGER NOT NULL DEFAULT 0,
  default_ai_tool TEXT,
  safe_notes TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (parent_project_key) REFERENCES projects(project_key)
);

CREATE INDEX IF NOT EXISTS idx_projects_status_priority
  ON projects(status, priority, project_label);

CREATE TABLE IF NOT EXISTS daily_top_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  project_key TEXT,
  reason TEXT,
  status TEXT NOT NULL DEFAULT 'active'
    CHECK (status IN ('active', 'queued', 'completed', 'removed')),
  sort_order INTEGER NOT NULL DEFAULT 0,
  pinned INTEGER NOT NULL DEFAULT 0 CHECK (pinned IN (0, 1)),
  source TEXT,
  source_suggestion_key TEXT,
  source_item_type TEXT,
  source_label TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  completed_at TEXT,
  FOREIGN KEY (project_key) REFERENCES projects(project_key)
);

CREATE INDEX IF NOT EXISTS idx_daily_top_items_status_sort
  ON daily_top_items(status, sort_order, created_at);

CREATE INDEX IF NOT EXISTS idx_daily_top_items_completed_at
  ON daily_top_items(completed_at);

CREATE UNIQUE INDEX IF NOT EXISTS idx_daily_top_items_source_suggestion_key
  ON daily_top_items(source_suggestion_key)
  WHERE source_suggestion_key IS NOT NULL;

CREATE TRIGGER IF NOT EXISTS trg_daily_top_items_active_limit_insert
BEFORE INSERT ON daily_top_items
WHEN
  NEW.status = 'active'
  AND (SELECT COUNT(*) FROM daily_top_items WHERE status = 'active') >= 3
BEGIN
  SELECT RAISE(ABORT, 'daily_top_items_active_limit');
END;

CREATE TRIGGER IF NOT EXISTS trg_daily_top_items_active_limit_update
BEFORE UPDATE OF status ON daily_top_items
WHEN
  NEW.status = 'active'
  AND OLD.status != 'active'
  AND (SELECT COUNT(*) FROM daily_top_items WHERE status = 'active') >= 3
BEGIN
  SELECT RAISE(ABORT, 'daily_top_items_active_limit');
END;

CREATE TABLE IF NOT EXISTS brief_suggestions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  suggestion_key TEXT NOT NULL UNIQUE,
  source TEXT NOT NULL CHECK (source IN ('woodcraft_brief_me')),
  source_label TEXT NOT NULL,
  briefing_date TEXT NOT NULL,
  source_item_type TEXT NOT NULL CHECK (source_item_type IN ('priority', 'next_action')),
  source_item_index INTEGER NOT NULL,
  title TEXT NOT NULL,
  reason TEXT,
  project_key TEXT,
  urgency TEXT,
  source_status TEXT,
  status TEXT NOT NULL DEFAULT 'pending'
    CHECK (status IN ('pending', 'accepted', 'ignored')),
  accepted_top_item_id INTEGER,
  imported_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  accepted_at TEXT,
  ignored_at TEXT,
  FOREIGN KEY (project_key) REFERENCES projects(project_key),
  FOREIGN KEY (accepted_top_item_id) REFERENCES daily_top_items(id)
);

CREATE INDEX IF NOT EXISTS idx_brief_suggestions_status_imported
  ON brief_suggestions(status, imported_at DESC);

CREATE INDEX IF NOT EXISTS idx_brief_suggestions_source_date_type
  ON brief_suggestions(source, briefing_date, source_item_type);

CREATE TABLE IF NOT EXISTS quick_captures (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  text TEXT NOT NULL,
  captured_at TEXT NOT NULL,
  project_key TEXT,
  capture_type TEXT,
  status TEXT,
  processed INTEGER NOT NULL DEFAULT 0 CHECK (processed IN (0, 1)),
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (project_key) REFERENCES projects(project_key)
);

CREATE INDEX IF NOT EXISTS idx_quick_captures_captured_at
  ON quick_captures(captured_at DESC);

CREATE INDEX IF NOT EXISTS idx_quick_captures_processed
  ON quick_captures(processed, captured_at DESC);

CREATE TABLE IF NOT EXISTS blocked_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_key TEXT,
  title TEXT NOT NULL,
  reason TEXT,
  status TEXT NOT NULL DEFAULT 'Blocked'
    CHECK (status IN ('Blocked', 'Needs Review', 'Resolved')),
  next_action TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  resolved_at TEXT,
  FOREIGN KEY (project_key) REFERENCES projects(project_key)
);

CREATE INDEX IF NOT EXISTS idx_blocked_items_status_created
  ON blocked_items(status, created_at DESC);

INSERT OR IGNORE INTO projects (
  project_key, project_label, parent_project_key, status, priority,
  default_ai_tool, safe_notes, created_at, updated_at
) VALUES
  ('dashboard-lifeops-command-center', 'Dashboard / LifeOps Command Center', NULL, 'Active', 10, 'Codex', NULL, '2026-06-27T00:00:00+00:00', '2026-06-27T00:00:00+00:00'),
  ('ai-tools-usage', 'AI Tools / Usage', NULL, 'Active', 20, 'Codex', NULL, '2026-06-27T00:00:00+00:00', '2026-06-27T00:00:00+00:00'),
  ('drakkar-designs', 'Drakkar Designs', NULL, 'Active', 30, NULL, NULL, '2026-06-27T00:00:00+00:00', '2026-06-27T00:00:00+00:00'),
  ('woodworking-cnc', 'Woodworking / CNC', NULL, 'Active', 40, NULL, NULL, '2026-06-27T00:00:00+00:00', '2026-06-27T00:00:00+00:00'),
  ('social-media-marketing', 'Social Media / Marketing', NULL, 'Active', 50, NULL, NULL, '2026-06-27T00:00:00+00:00', '2026-06-27T00:00:00+00:00'),
  ('finance-admin', 'Finance / Admin', NULL, 'Active', 60, NULL, NULL, '2026-06-27T00:00:00+00:00', '2026-06-27T00:00:00+00:00'),
  ('books-projects', 'Books Projects', NULL, 'Active', 70, NULL, NULL, '2026-06-27T00:00:00+00:00', '2026-06-27T00:00:00+00:00'),
  ('wow-gaming', 'WoW / Gaming', NULL, 'Active', 80, NULL, NULL, '2026-06-27T00:00:00+00:00', '2026-06-27T00:00:00+00:00'),
  ('home-tech', 'Home / Tech', NULL, 'Active', 90, NULL, NULL, '2026-06-27T00:00:00+00:00', '2026-06-27T00:00:00+00:00'),
  ('other-unsorted', 'Other / Unsorted', NULL, 'Active', 100, NULL, NULL, '2026-06-27T00:00:00+00:00', '2026-06-27T00:00:00+00:00');
