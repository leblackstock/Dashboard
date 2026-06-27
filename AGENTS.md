# Dashboard Agent Instructions

Current approved master spec: `dashboard_master_spec_v4.46.md`.

If the root spec and `docs/dashboard_master_spec_v4.46.md` ever differ, use the newest approved master spec as authoritative.

## Current Status

Phase 1 is complete, pushed, and tagged:

- Repo: `https://github.com/leblackstock/Dashboard`
- Branch: `main`
- Tag: `phase1-codex-usage-v0.1.0`
- Commit: `f377a6937cb9f781700c74bf024f302f292fb1e4`

Phase 2 implementation is approved with the scope below.

## Phase 2 Scope Lock

Implement Phase 2 only:

- Daily Command Center v1.
- Existing Codex Usage card carried forward.
- Today’s Top 3, Active Projects, Blocked / Needs Review, Quick Capture, and Collector Health cards.
- Project Registry v1.
- Basic dark/glow frontend polish.

Do not add Claude/ChatGPT collectors, best-AI-tool recommendations, Weekly/Monthly dashboards, draggable/resizable grids, calendar/email integrations, notifications, mobile/PWA polish, external hosting, multi-user auth, a scheduler/background collector, MCP tools, token proxy tools, autonomous memory, or a new database without explicit approval.

## Phase 2 Clarifications

- Today’s Top 3 shows all non-completed items.
- Today’s Top 3 also shows items completed today, collapsed/faded.
- Today’s Top 3 hides items completed before today by default.
- Do not add calendar/recurrence behavior in Phase 2.
- Quick Capture raw text means user-entered local note/capture text only.
- Quick Capture must not become an import path for raw logs, raw endpoint payloads, prompt history, auth files, rollout files, or pasted secret dumps.

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
