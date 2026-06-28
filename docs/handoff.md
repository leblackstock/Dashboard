# Dashboard Handoff

## Current Status

Current project status reference: `dashboard_master_spec_v4.50.md`.

Published repository state:

- Repo: `https://github.com/leblackstock/Dashboard`
- Branch: `main`
- Commit: `eff205f490192c6e0a8f9c817495251a9d4e9419`
- Tag: `phase2-daily-usability-polish-v0.2.5`

Phase 2.5 is complete and published. Current local work is Phase 2.6: Persistent Local Dashboard Runtime.

## Phase 2.6 Scope

- Install or uninstall one owned current-user Windows Scheduled Task for dashboard startup at logon.
- Keep manual start, stop, restart, and status behavior intact.
- Start the local web app only; do not schedule collectors or AI work.
- Use only built-in PowerShell and Windows Task Scheduler support.
- Add optional Taskfile aliases while keeping direct PowerShell commands authoritative.
- Document manual startup, login startup, removal, status, and occupied-port troubleshooting.

Do not add scheduled collectors, provider collectors, recommendations/scoring, notifications, integrations, hosting/auth, major UI redesign, a Windows service, NSSM, or new dependencies.

## Safety Reminder

Do not print, store, commit, return, or render raw tokens, refresh tokens, cookies, authorization headers, auth contents, raw endpoint payloads, prompt previews, raw logs, rollout files, or full workspace paths.

Process state may contain only validated PIDs, process names, and start times. The supervisor must never stop unrelated processes.

## Acceptance Gate

1. Exercise `install-task`, `status`, `stop`, `start`, `restart`, and `uninstall-task`.
2. Confirm health, Daily API, and frontend HTTP `200` responses.
3. Confirm install/uninstall changes only the exact owned task and succeeds without elevation.
4. Confirm stopping does not terminate unrelated listeners and occupied ports fail safely.
5. Run pytest, Ruff, frontend build, Gitleaks, `git diff --check`, and gitignore checks.
6. Keep local-only master spec references uncommitted.
