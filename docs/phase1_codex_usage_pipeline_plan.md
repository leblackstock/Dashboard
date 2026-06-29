# Phase 1 Codex Usage Pipeline Plan

Current master spec: `dashboard_master_spec_v4.52.md`

Approved decisions have been applied to this plan. Do not start coding until a separate implementation request is given.

## A. Revised Phase 1 Plan

Build Phase 1 only as the smallest complete working pipeline:

```txt
Codex live usage collector
→ sanitized JSON snapshot
→ SQLite row
→ FastAPI endpoint
→ one frontend Codex Usage card
```

Phase 1 includes:

- Repo skeleton and repo-quality guardrails from the current approved master spec.
- Codex live usage collector using the confirmed `/wham/usage` source.
- Safe Codex auth reader that keeps tokens in memory only.
- Sanitized mapper and JSON snapshot writer.
- SQLite schema/init and insert/update path.
- Collector run logging with safe messages only.
- FastAPI health endpoint and `GET /api/ai/codex/live-usage`.
- One React/Vite/TypeScript Codex Usage card.
- Startup/run support and quick docs/runbook.
- Basic pytest structure, Ruff config, and secret-scan command.
- Fake fixtures only.
- Generated sanitized JSON snapshots are gitignored by default; keep only `data/sanitized/codex/.gitkeep`.
- Copy/reference the current master spec under `docs/`; if specs ever differ, the newest approved master spec is authoritative.

Do not build Phase 2 features:

- Daily dashboard cards.
- Project registry UI.
- Draggable/resizable grid.
- Scheduled collectors.
- Claude or ChatGPT collectors.
- Recommendation engine.
- Notifications.
- Calendar/email integrations.
- Full mobile/PWA polish.
- MCP server.
- Token proxy tools.
- Autonomous memory.
- SaaS/full-stack mega template.
- Cloud deployment.
- External auth/Auth0.
- Postgres, Docker, or Alembic unless later approved.

## B. Skills/tools Recommended

Use targeted skills only:

- `utf8-no-mojibake` for Markdown/text edits.
- Planning/review skill for scope and implementation review.
- FastAPI structure skill if available and lightweight.
- SQLite/schema skill if available and lightweight.
- Python collector/CLI script skill if available and directly relevant.
- React/Vite/Tailwind/shadcn card UI skill if available and directly relevant.
- Security/secrets review workflow before any commit or handoff.
- Testing/review skill for collector, DB, API, and frontend checks.
- Handoff/session-summary skill for `docs/handoff.md`.
- Repo-instructions/AGENTS.md skill for `AGENTS.md`.
- Context compression/token-efficiency skill for long sessions only.

Recommended tooling:

- Python: `uv`, FastAPI, SQLite using `schema.sql`, `pydantic-settings`, pytest, Ruff.
- Collector CLI: plain Python first; Typer only if subcommands become useful.
- Frontend: React + Vite + TypeScript + Tailwind + shadcn/ui.
- Frontend data: TanStack Query.
- Icons: Lucide React.
- Charts: Recharts later, not required for the first card.
- Package manager: pnpm.
- Task runner: `Taskfile.yml`.
- Secret scanning: Gitleaks early; TruffleHog optional/manual deeper scan.
- API types: Hey API / Orval only after the first endpoint stabilizes.
- Python project files: prefer `pyproject.toml` + `uv.lock`; do not add `requirements.txt` unless there is a clear reason.

Skills/reference rules:

- Search available/local skills before building from scratch.
- Use only targeted skills that directly help Phase 1.
- Do not bulk-install a skill pack.
- Do not add overlapping or action-capable skills without approval.

Reference repos/docs:

- Use `satnaing/shadcn-admin` only as UI/card/layout reference.
- Use the FastAPI full-stack template only as backend organization reference.
- Use official docs and skill catalogs as references.
- Do not clone or adopt a large template wholesale.

Self-learning/token-efficiency rules:

- Use repo-local learning only: `AGENTS.md`, handoff summaries, decisions log, runbook updates, and short reviewed project memory.
- Do not add hidden autonomous memory, screenshot/screen memory, background recall, self-modifying agents, raw transcript memory, token proxies, MCP tools, or self-evolving frameworks without explicit approval.
- Use targeted file search, repo-map behavior, context compression for handoffs, concise command-output summaries, and security-aware log summarization.

## C. Skills/tools/templates To Skip

Skip unless explicitly approved:

- Large SaaS/full-stack templates.
- FastAPI full-stack template as an implementation base.
- `satnaing/shadcn-admin` as a clone/template.
- Postgres, Docker, Alembic, Traefik, or Caddy.
- Cloud deployment.
- External auth systems such as Auth0.
- Billing/subscription frameworks.
- RAG/vector databases.
- MCP server.
- Token proxy tools.
- Scheduled collectors.
- Autonomous memory, background recall, or screen/screenshot memory.
- External action skills.
- Overlapping frontend design skills.
- Claude/ChatGPT collectors.
- `justfile`.
- Any skill/tool that encourages storing raw payloads, auth headers, or secrets.

Use references only:

- `satnaing/shadcn-admin` for card/layout ideas.
- FastAPI full-stack template for backend organization ideas only.
- Official docs and curated skill catalogs as reference/search sources.

## D. Updated Build Order

1. Create repo skeleton and copy/reference the current approved master spec.
2. Add repo-quality files: `AGENTS.md`, `.gitignore`, `.env.example`, `.gitleaks.toml`, `docs/runbook.md`, `docs/decisions.md`, `docs/handoff.md`, `Taskfile.yml`.
3. Set up backend project with `uv`, `pyproject.toml`, `uv.lock`, FastAPI, `pydantic-settings`, pytest, and Ruff.
4. Add SQLite `schema.sql` for `ai_accounts`, `ai_usage_snapshots`, and `collector_runs`.
5. Add settings, DB helper, and init path.
6. Add safe Codex auth reader.
7. Add Codex usage mapper using sanitized fields only.
8. Add live usage collector calling `/wham/usage`.
9. Add sanitized JSON writer under `data/sanitized/codex/`; commit only `.gitkeep`, not generated snapshots.
10. Add SQLite account upsert and usage snapshot insert.
11. Add collector run logging with safe messages only.
12. Add FastAPI health endpoint and Codex usage endpoint.
13. Set up frontend with pnpm, Vite, React, TypeScript, Tailwind, shadcn/ui, TanStack Query, and Lucide React.
14. Build one Codex Usage card.
15. Add fake fixtures and tests under `backend/tests/fixtures/`.
16. Run Ruff, pytest, frontend checks, and Gitleaks scan using `.gitleaks.toml`.
17. Update runbook/startup docs and handoff.

## E. Security Checks

Verify no raw secrets appear in console output, JSON, SQLite, API responses, frontend props, docs, logs, fixtures, or committed files.

Never print, log, export, store, commit, or expose:

- Access tokens.
- Refresh tokens.
- Cookies.
- Authorization headers.
- Auth file contents.
- Raw endpoint payloads in the dashboard DB or exports.
- Prompt previews.
- First user messages.
- Raw logs.
- Raw rollout files.
- Full workspace paths by default.

Allowed:

- Sanitized snapshots.
- Hashed account keys.
- Local-only account labels.
- Safe project labels.
- Aggregate usage metrics.
- Freshness/confidence metadata.
- Temporary local debug capture only if manually enabled, short-lived, and never containing auth secrets.

Required checks:

- Collector console output contains only sanitized status and aggregate fields.
- Sanitized JSON contains only approved fields.
- SQLite rows contain only approved fields.
- API response contains only sanitized grouped account data.
- Frontend card renders only sanitized API fields.
- Fake fixtures contain fake tokens/payloads only.
- Gitleaks scan runs before any commit or handoff using `.gitleaks.toml`.
- TruffleHog can be run manually for deeper review if needed.

## F. File List

Expected files to create or modify:

- `AGENTS.md`
- `.gitignore`
- `.env.example`
- `.gitleaks.toml`
- `Taskfile.yml`
- `pyproject.toml`
- `uv.lock`
- `backend/app/main.py`
- `backend/app/db.py`
- `backend/app/settings.py`
- `backend/app/models.py`
- `backend/app/routes/ai_codex.py`
- `backend/collectors/codex_auth.py`
- `backend/collectors/codex_usage_mapper.py`
- `backend/collectors/collect_codex_live_usage.py`
- `backend/db/schema.sql`
- `backend/tests/`
- `backend/tests/fixtures/`
- `frontend/index.html`
- `frontend/package.json`
- `frontend/pnpm-lock.yaml`
- `frontend/vite.config.ts`
- `frontend/tsconfig.json`
- `frontend/tailwind.config.js`
- `frontend/src/App.tsx`
- `frontend/src/main.tsx`
- `frontend/src/components/CodexUsageCard.tsx`
- `frontend/src/lib/api.ts`
- `frontend/src/lib/types.ts`
- `frontend/src/styles.css`
- `data/sanitized/codex/.gitkeep`
- `docs/runbook.md`
- `docs/decisions.md`
- `docs/handoff.md`
- `docs/phase1_quick_start.md`
- `docs/dashboard_master_spec_v4.52.md`

Generated/local-only, gitignored:

- SQLite DB files.
- Generated sanitized JSON snapshots.
- Logs.
- Raw/debug folders.
- `.env`.

Not expected unless a clear reason is approved:

- `requirements.txt`
- `justfile`

## G. Questions Or Approvals Needed Before Coding

Approved decisions:

- Use `Taskfile.yml`, not `justfile`.
- Use `uv` for Python dependency/project management.
- Use React + Vite + TypeScript + Tailwind + shadcn/ui for the Phase 1 frontend.
- Gitignore generated sanitized JSON snapshots by default; keep only `data/sanitized/codex/.gitkeep`.
- Copy/reference the current master spec under `docs/`; if specs ever differ, the newest approved master spec is authoritative.
- Prefer `pyproject.toml` + `uv.lock`; do not add `requirements.txt` unless there is a clear reason.
- Do not add any new major package, framework, service, template, MCP tool, scheduler, auth system, database, or external integration beyond this plan without stopping and asking first.

Open questions:

- None for this plan update.
- Implementation should begin only after an explicit request to start coding.
