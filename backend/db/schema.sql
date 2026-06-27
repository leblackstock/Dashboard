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
