CREATE TABLE daily_top_items_phase_2_7 (
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

INSERT INTO daily_top_items_phase_2_7 (
  id, title, project_key, reason, status, sort_order, pinned,
  source, source_suggestion_key, source_item_type, source_label,
  created_at, updated_at, completed_at
)
WITH ordered_open AS (
  SELECT
    id,
    ROW_NUMBER() OVER (
      ORDER BY pinned DESC, sort_order ASC, created_at ASC, id ASC
    ) AS visible_position
  FROM daily_top_items
  WHERE status != 'completed'
)
SELECT
  item.id,
  item.title,
  item.project_key,
  item.reason,
  CASE
    WHEN item.status = 'completed' THEN 'completed'
    WHEN ordered.visible_position <= 3 THEN 'active'
    ELSE 'queued'
  END,
  CASE
    WHEN item.status = 'completed' THEN item.sort_order
    WHEN ordered.visible_position <= 3 THEN ordered.visible_position - 1
    ELSE ordered.visible_position - 4
  END,
  item.pinned,
  suggestion.source,
  suggestion.suggestion_key,
  suggestion.source_item_type,
  suggestion.source_label,
  item.created_at,
  item.updated_at,
  item.completed_at
FROM daily_top_items AS item
LEFT JOIN ordered_open AS ordered
  ON ordered.id = item.id
LEFT JOIN brief_suggestions AS suggestion
  ON suggestion.accepted_top_item_id = item.id;

DROP TABLE daily_top_items;
ALTER TABLE daily_top_items_phase_2_7 RENAME TO daily_top_items;
