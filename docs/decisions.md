# Dashboard Decisions

## 2026-06-27 — Phase 1 Stack And Scope

- Use `dashboard_master_spec_v4.41.md` as the current approved master spec.
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
