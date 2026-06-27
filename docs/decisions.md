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
