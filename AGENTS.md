# Dashboard Agent Instructions

Current project status reference: `dashboard_master_spec_v4.50.md`.

The v4.50 file may be supplied as an untracked local reference. Do not commit local-only master spec files unless explicitly asked. If approved specs differ, the newest approved spec is authoritative.

## Current Status

Published repository: `https://github.com/leblackstock/Dashboard`

- Branch: `main`
- Current published commit: `7549e9d0cf508b131a0220e9981ada3b4e9b67d1`
- Brief/layout tag: `phase2-brief-suggestions-layout-v0.2.3`
- Codex account-label tag: `phase2-codex-account-labels-v0.2.4`

Current work is Phase 2.5: Daily Usability Polish.

## Phase 2.5 Scope Lock

In scope:

- Native PowerShell start/stop/restart/status supervisor.
- Thin optional Taskfile aliases.
- Gitignored process state under `.run/`.
- Optional local Woodcraft Brief source configured only through ignored `.env`.
- Runbook and handoff updates.
- Small layout reset, persistence, spacing, wrapping, and safe-message polish.

Do not add a scheduler, autostart task, scheduled collector, new provider collector, recommendation/scoring feature, notification, calendar/email integration, hosting/auth feature, major UI redesign, new layout package, or new dependency without explicit approval.

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

Taskfile aliases are optional and must not be required:

- `task dashboard:start`
- `task dashboard:stop`
- `task dashboard:restart`
- `task dashboard:status`

Existing setup and verification commands remain in `Taskfile.yml`. Use `uv` for Python and pnpm for the frontend. Use `Taskfile.yml`, not `justfile`.
