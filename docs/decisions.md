# Dashboard Decisions

## 2026-06-27 — Phase 1 Stack And Scope

- Phase 1 was implemented and published from `dashboard_master_spec_v4.41.md`; the current approved master spec is now `dashboard_master_spec_v4.46.md`.
- Implement Phase 1 only: Codex collector, sanitized snapshot, SQLite row, FastAPI endpoint, one Codex Usage card, startup/run support, and docs.
- Use `Taskfile.yml`, not `justfile`.
- Use `uv` with `pyproject.toml` and `uv.lock`; do not add `requirements.txt` unless there is a clear reason.
- Use React + Vite + TypeScript + Tailwind + shadcn/ui patterns for the frontend.
- Use pnpm for frontend package management.
- Gitignore generated sanitized JSON snapshots by default and keep only `data/sanitized/codex/.gitkeep`.
- Copy/reference the current master spec under `docs/`; if specs ever differ, the newest approved master spec is authoritative.
- Do not add any new major package, framework, service, template, MCP tool, scheduler, auth system, database, or external integration beyond the approved plan without stopping and asking first.

## 2026-06-27 — Security Defaults

- Codex auth is read in memory only.
- Raw tokens, refresh tokens, cookies, authorization headers, auth file contents, prompt previews, raw logs, raw endpoint payloads, and full workspace paths are never printed, stored, committed, returned by API, or shown in the frontend.
- Allowed stored data is limited to sanitized snapshots, hashed account keys, local-only account labels, aggregate usage metrics, and freshness/confidence metadata.

## 2026-06-27 — Phase 1 Published Checkpoint

- Phase 1 is complete, pushed, and tagged.
- Published repo: `https://github.com/leblackstock/Dashboard`
- Published branch: `main`
- Published tag: `phase1-codex-usage-v0.1.0`
- Published commit: `f377a6937cb9f781700c74bf024f302f292fb1e4`
- `dashboard_master_spec_v4.46.md` is now the current approved master spec.

## 2026-06-27 — Phase 2 Planning Defaults

- Phase 2 target: `Daily Command Center v1`.
- Project registry starts as SQLite table only.
- Card order starts as Codex Usage, Today’s Top 3, Active Projects, Blocked / Needs Review, Quick Capture, Collector Health.
- Today’s Top 3 is manual-first and carries forward until completed.
- Project/task cards are manual-first.
- Quick Capture stores raw capture text locally and classifies later.
- Collectors stay manual unless Phase 1 collector remains stable and clean.
- UI starts clean/simple, with premium polish added gradually.
- Phase 2 stops when the Daily dashboard is useful.

## 2026-06-27 — Phase 2 Approval Clarifications

- Phase 2 implementation is approved for `Daily Command Center v1`.
- Today’s Top 3 shows all non-completed items.
- Today’s Top 3 also shows items completed today, collapsed/faded.
- Today’s Top 3 hides items completed before today by default.
- Do not add calendar/recurrence behavior in Phase 2.
- Quick Capture raw text means user-entered local note/capture text only.
- Quick Capture must not become an import path for raw logs, raw endpoint payloads, prompt history, auth files, rollout files, or pasted secret dumps.

## 2026-06-27 — Phase 2.3 And 2.4 Published Checkpoints

- `phase2-brief-suggestions-layout-v0.2.3` points to `9cfa6c33345596f22820677326ee81ad9af177b5`.
- `phase2-codex-account-labels-v0.2.4` points to `7549e9d0cf508b131a0220e9981ada3b4e9b67d1`.
- Current published `main` is `7549e9d0cf508b131a0220e9981ada3b4e9b67d1`.
- Brief Suggestions, flexible masonry layout, header dragging, persistence/reset, multi-account Codex usage, safe account labels, and quota reset clocks are published.

## 2026-06-28 — Phase 2.5 Daily Usability Polish

- Use `scripts/dashboard.ps1` as the primary Windows start/stop/restart/status supervisor.
- Add Taskfile aliases, but do not require Task to be installed.
- Store only validated PID/process-name/start-time state under gitignored `.run/`.
- Never stop a process unless its saved identity is validated; occupied ports must fail safely.
- Keep `WOODCRAFT_BRIEF_SOURCE` optional and blank in `.env.example`.
- Store the real Brief path only in ignored local `.env`; never return or display it.
- Keep the existing masonry layout and limit UI changes to reset, persistence, spacing, wrapping, and safe-message polish.
- Do not add dependencies, scheduling/autostart, provider collectors, Phase 3 intelligence, integrations, hosting/auth, or a major redesign.

## 2026-06-28 — Phase 2.5 Published Checkpoint

- `phase2-daily-usability-polish-v0.2.5` points to `eff205f490192c6e0a8f9c817495251a9d4e9419`.
- Current published `main` is `eff205f490192c6e0a8f9c817495251a9d4e9419`.
- Native PowerShell dashboard lifecycle commands, Taskfile aliases, safe local Brief configuration, runbook improvements, and small UI polish are published.

## 2026-06-28 — Phase 2.6 Persistent Local Dashboard Runtime

- Add one current-user Windows Scheduled Task named `Dashboard Local Runtime` using built-in PowerShell ScheduledTasks cmdlets.
- Trigger the task at current-user logon with an interactive, limited-run-level principal; administrator privileges are not required.
- The task action may only call `scripts/dashboard.ps1 start`; it must not run collectors or add AI automation.
- Mark ownership with an exact description and refuse to overwrite or remove a same-name task without that marker.
- Installing starts the task once for immediate verification. Uninstalling removes only the managed task and does not stop the dashboard.
- Keep `.run/` as the only local process-state location and preserve PID, process-name, and start-time validation before stopping process trees.
- Add no dependency, Windows service, NSSM integration, scheduled collector, or Phase 3 feature.

## 2026-06-29 — Master Spec v4.52 Replacement

- `dashboard_master_spec_v4.52.md` is the active approved master spec.
- It replaces `dashboard_master_spec_v4.46.md` at both the repository root and under `docs/`.
- Replaced master spec files may be removed instead of retained alongside the active spec.
- Phase 2.6 is published at `b3d1c805f45f587135fac3b93e29d1db8ca58f1f` with tag `phase2-persistent-dashboard-runtime-v0.2.6`.
- Phase 2.7 Top 3 Priority Controls is approved for implementation after this documentation alignment commit.
