# Dashboard Agent Instructions

Current approved master spec: `dashboard_master_spec_v4.38.md`.

If the root spec and `docs/dashboard_master_spec_v4.38.md` ever differ, use the newest approved master spec as authoritative.

## Phase 1 Scope Lock

Implement Phase 1 only:

- Codex live usage collector.
- Sanitized JSON snapshot.
- SQLite row.
- FastAPI endpoint.
- One frontend Codex Usage card.
- Startup/run support.
- Quick docs/runbook.

Do not add Phase 2 cards, project registry UI, draggable grids, scheduled collectors, other AI collectors, recommendations, notifications, calendar/email integrations, cloud deployment, external auth, MCP tools, token proxy tools, autonomous memory, or a new database without explicit approval.

## Security Rules

Never print, log, export, store, commit, return from the API, or show in the frontend:

- Access tokens.
- Refresh tokens.
- Cookies.
- Authorization headers.
- Auth file contents.
- Raw endpoint payloads.
- Prompt previews.
- First user messages.
- Raw logs.
- Raw rollout files.
- Full workspace paths by default.

Allowed outputs are sanitized snapshots, hashed account keys, local-only account labels, safe project labels, aggregate usage metrics, and freshness/confidence metadata.

## Commands

- Backend setup: `task backend:sync`
- Initialize DB: `task db:init`
- Run collector manually: `task collector:codex`
- Start backend: `task backend:dev`
- Frontend setup: `task frontend:install`
- Start frontend: `task frontend:dev`
- Tests: `task test`
- Lint: `task lint`
- Secret scan: `task scan:secrets`

Use `uv` for Python and pnpm for the frontend. Use `Taskfile.yml`, not `justfile`.
