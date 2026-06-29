# Dashboard Agent Instructions

Current approved master spec: `dashboard_master_spec_v4.52.md`.

The root spec and `docs/dashboard_master_spec_v4.52.md` must match. When an approved master spec replaces an older one, remove the replaced root/docs copies unless there is a specific reason to retain them.

## Current Status

Published repository: `https://github.com/leblackstock/Dashboard`

- Branch: `main`
- Current published commit: `b3d1c805f45f587135fac3b93e29d1db8ca58f1f`
- Current published tag: `phase2-persistent-dashboard-runtime-v0.2.6`

Current work is Phase 2.7: Top 3 Priority Controls.

## Phase 2.7 Scope Lock

In scope:

- Maximum three active Today’s Top 3 items.
- Manual overflow and accepted Brief overflow routed to a collapsed Priority Queue.
- Manual queue promotion with no automatic promotion after completion/removal.
- Active item drag/reorder with persistent `sort_order`.
- Remove from Today without completion/deletion.
- Return to Suggestions only for Brief-linked items.
- Sanitized Brief source tracking and durable dedupe.

Do not add delete/trash behavior, scheduled collectors, new provider collectors, Phase 3 recommendation/scoring, notifications, calendar/email integrations, hosting/auth, a major redesign, a new layout package, or a new dependency without explicit approval.

## Safety Rules

Never print, log, export, store, commit, return from the API, or show in the frontend:

- Access tokens or refresh tokens.
- Cookies or authorization headers.
- Auth file contents or raw endpoint payloads.
- Prompt previews or first user messages.
- Raw logs or rollout files.
- Full workspace paths by default.

Allowed outputs are sanitized snapshots, hashed account keys, local-only account labels, safe project labels, aggregate usage metrics, freshness/confidence metadata, safe process status, and local service URLs.

## Commands

Primary Windows lifecycle commands:

- Start: `.\scripts\dashboard.ps1 start`
- Stop: `.\scripts\dashboard.ps1 stop`
- Restart: `.\scripts\dashboard.ps1 restart`
- Status: `.\scripts\dashboard.ps1 status`
- Install at login: `.\scripts\dashboard.ps1 install-task`
- Uninstall login task: `.\scripts\dashboard.ps1 uninstall-task`

Taskfile aliases are optional and must not be required:

- `task dashboard:start`
- `task dashboard:stop`
- `task dashboard:restart`
- `task dashboard:status`
- `task dashboard:install-task`
- `task dashboard:uninstall-task`

Existing setup and verification commands remain in `Taskfile.yml`. Use `uv` for Python and pnpm for the frontend. Use `Taskfile.yml`, not `justfile`.
