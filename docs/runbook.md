# Dashboard Runbook

Current approved master spec: `dashboard_master_spec_v4.46.md`.

Published Phase 1 checkpoint:

- Repo: `https://github.com/leblackstock/Dashboard`
- Branch: `main`
- Tag: `phase1-codex-usage-v0.1.0`
- Commit: `f377a6937cb9f781700c74bf024f302f292fb1e4`

Phase 1 builds only this pipeline:

```txt
Codex live usage collector
→ sanitized JSON snapshot
→ SQLite row
→ FastAPI endpoint
→ one frontend Codex Usage card
```

## Setup

The preferred command runner is Taskfile. If the `task` command is not installed, run the commands listed inside `Taskfile.yml` directly.

Install Python dependencies:

```powershell
task backend:sync
```

Install frontend dependencies:

```powershell
task frontend:install
```

The Taskfile invokes a pinned pnpm runner through `npx` so the command works even when pnpm is not installed globally.

## Initialize Database

```powershell
task db:init
```

The default database is `data/dashboard.db`. Generated database files are local-only and gitignored.

## Run Collector Manually

```powershell
task collector:codex
```

The collector reads Codex auth in memory only, calls the live usage endpoint, writes a sanitized snapshot to `data/sanitized/codex/latest.json`, inserts sanitized rows into SQLite, and records a safe collector status.

Do not enable scheduled collection until manual runs are verified safe.

## Start Backend

```powershell
task backend:dev
```

Health check:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/health
```

Codex usage endpoint:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/ai/codex/live-usage
```

## Start Frontend

```powershell
task frontend:dev
```

Open the local Vite URL shown by pnpm. The first screen is the Daily dashboard. In Phase 1 it showed only the Codex Usage card; in Phase 2 it expands into `Daily Command Center v1`.

## Verification

Run backend tests:

```powershell
task test
```

Run lint:

```powershell
task lint
```

Build frontend:

```powershell
task frontend:build
```

Run a redacted secret scan:

```powershell
task scan:secrets
```

This requires Gitleaks to be installed on PATH. If it is unavailable, install Gitleaks before treating the secret-scan gate as complete.

Confirm that no tokens, cookies, authorization headers, auth file contents, raw endpoint payloads, prompt previews, raw logs, or full workspace paths appear in console output, snapshots, SQLite, API responses, frontend props, docs, or committed files.

## Startup Notes

Phase 1 may use Windows Task Scheduler for the backend only after manual backend startup works. Do not add a scheduled collector until the manual collector is proven safe and explicitly approved.

## Phase 2

Phase 2 implementation is approved. See `docs/phase2_implementation_plan.md`.

Phase 2 keeps the Codex collector manual and adds a local-first Daily dashboard with Codex Usage, Today’s Top 3, Active Projects, Blocked / Needs Review, Quick Capture, and Collector Health.

Today’s Top 3 shows all non-completed items, also shows items completed today collapsed/faded, and hides items completed before today by default. Phase 2 does not add calendar or recurrence behavior.

Quick Capture stores only user-entered local note/capture text. It must not ingest raw logs, raw endpoint payloads, prompt history, auth files, rollout files, or pasted secret dumps.
