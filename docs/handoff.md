# Dashboard Handoff

## Current Status

Current project status reference: `dashboard_master_spec_v4.50.md`.

Published repository state:

- Repo: `https://github.com/leblackstock/Dashboard`
- Branch: `main`
- Commit: `7549e9d0cf508b131a0220e9981ada3b4e9b67d1`
- Tag: `phase2-brief-suggestions-layout-v0.2.3`
- Tag: `phase2-codex-account-labels-v0.2.4`

Phase 2.3/2.4 is complete and published. Current work is Phase 2.5: Daily Usability Polish.

## Phase 2.5 Scope

- One-command native PowerShell startup for backend and frontend.
- Safe start, stop, restart, and status behavior using gitignored process state.
- Optional Taskfile aliases; Task must not be required.
- Optional Woodcraft Brief source configured only in ignored `.env`.
- Safe unconfigured/missing/invalid Brief responses with no local path exposure.
- Small layout reset, persistence, spacing, wrapping, and status-message polish.
- Runbook and decision updates.

Do not add scheduling, autostart, provider collectors, recommendations/scoring, notifications, integrations, hosting/auth, major UI redesign, or new dependencies.

## Safety Reminder

Do not print, store, commit, return, or render raw tokens, refresh tokens, cookies, authorization headers, auth contents, raw endpoint payloads, prompt previews, raw logs, rollout files, or full workspace paths.

Process state may contain only validated PIDs, process names, and start times. The supervisor must never stop unrelated processes.

## Acceptance Gate

1. Exercise `start`, `status`, `restart`, and `stop`.
2. Confirm health, Daily API, and frontend HTTP `200` responses.
3. Confirm occupied ports are rejected without stopping their owners.
4. Test unset, missing, invalid, and valid Brief configuration.
5. Browser-test drag persistence, reset, Brief actions, forms, and Codex refresh.
6. Run pytest, Ruff, frontend build, Gitleaks, `git diff --check`, and gitignore checks.
7. Keep local `dashboard_master_spec_v4.50.md` uncommitted.
