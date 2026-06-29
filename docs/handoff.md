# Dashboard Handoff

## Current Status

Current project status reference: `dashboard_master_spec_v4.52.md`.

Published repository state:

- Repo: `https://github.com/leblackstock/Dashboard`
- Branch: `main`
- Commit: `b3d1c805f45f587135fac3b93e29d1db8ca58f1f`
- Tag: `phase2-persistent-dashboard-runtime-v0.2.6`

Phase 2.6 is complete and published. Current work is Phase 2.7: Top 3 Priority Controls.

## Phase 2.7 Scope

- Enforce no more than three active Today’s Top 3 items.
- Route manual and accepted Brief overflow to a collapsed Priority Queue.
- Keep queue promotion manual and reject promotion while active Top 3 is full.
- Persist active item ordering with `sort_order`.
- Support Remove from Today without completion/deletion.
- Support Return to Suggestions only for Brief-linked items.
- Preserve Brief dedupe across accepted, queued, completed, removed, and ignored states.

Do not add delete/trash behavior, scheduled collectors, provider collectors, Phase 3 recommendations/scoring, notifications, integrations, hosting/auth, a major redesign, or new dependencies.

## Safety Reminder

Do not print, store, commit, return, or render raw tokens, refresh tokens, cookies, authorization headers, auth contents, raw endpoint payloads, prompt previews, raw logs, rollout files, or full workspace paths.

Process state may contain only validated PIDs, process names, and start times. The supervisor must never stop unrelated processes.

## Acceptance Gate

1. Test manual and Brief acceptance below and at the three-active-item limit.
2. Test collapsed queue, manual promotion, remove, return, and Brief dedupe.
3. Test active item drag/reorder persistence and refresh/reload persistence.
4. Confirm `/api/daily` remains sanitized and removed items stay hidden.
5. Run pytest, Ruff, frontend build, Gitleaks, `git diff --check`, and gitignore checks.
