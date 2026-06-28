# Dashboard Runbook

Current project status reference: `dashboard_master_spec_v4.50.md`.

Published checkpoint:

- Repo: `https://github.com/leblackstock/Dashboard`
- Branch: `main`
- Commit: `7549e9d0cf508b131a0220e9981ada3b4e9b67d1`
- Tags: `phase2-brief-suggestions-layout-v0.2.3`, `phase2-codex-account-labels-v0.2.4`

Local-only master spec files are references and must not be committed unless explicitly approved.

## Initial Setup

Install backend dependencies:

```powershell
uv sync
```

Install frontend dependencies:

```powershell
Set-Location frontend
npx pnpm@9.15.9 install
Set-Location ..
```

Initialize the local database:

```powershell
uv run python -m backend.app.db --init
```

Generated databases, snapshots, frontend builds, dependencies, logs, and process state are local-only and gitignored.

## Local Configuration

Create local `.env` from `.env.example` only when `.env` does not already exist. Keep `.env` ignored.

The Woodcraft Brief source is optional. To enable manual Brief Suggestions import, set this only in local `.env`:

```dotenv
WOODCRAFT_BRIEF_SOURCE=<local path to approved brief_latest.json>
```

Do not put tokens, cookies, authorization headers, auth contents, or raw payloads in `.env`. The configured Brief path is never returned by the API or shown in the frontend.

## Daily Start

The primary Windows command starts backend and frontend together:

```powershell
.\scripts\dashboard.ps1 start
```

The supervisor:

- Refuses to start when required ports are occupied.
- Starts both services in the background.
- Stores only process IDs, process names, and start times under gitignored `.run/`.
- Verifies backend health, the Daily API, and the frontend before reporting success.
- Never stops a process unless its saved identity is validated.

Open:

```txt
http://127.0.0.1:5173/
```

## Status, Restart, And Stop

```powershell
.\scripts\dashboard.ps1 status
.\scripts\dashboard.ps1 restart
.\scripts\dashboard.ps1 stop
```

`stop` only targets validated process trees created by the supervisor. If a saved PID no longer matches, the script reports that it was not stopped.

## Optional Taskfile Aliases

When Task is installed, these aliases call the same PowerShell supervisor:

```powershell
task dashboard:start
task dashboard:status
task dashboard:restart
task dashboard:stop
```

Task is optional. The direct PowerShell commands remain supported and authoritative.

## Individual Development Commands

Use these when foreground logs are needed for debugging:

```powershell
uv run uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

```powershell
Set-Location frontend
npx pnpm@9.15.9 dev -- --host 127.0.0.1 --port 5173
```

Do not run the supervisor on the same ports while individual development servers are active.

## Manual Collectors

Codex usage remains manual:

```powershell
uv run python -m backend.collectors.collect_codex_live_usage
```

Woodcraft Brief Suggestions remain manual through `Refresh Brief Suggestions` in the UI. No scheduler or background collector is enabled.

## Health Checks

```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/api/health
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/api/daily
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:5173/
```

Each should return HTTP `200` while the dashboard is running.

## Verification

```powershell
uv run pytest
uv run ruff check .
Set-Location frontend
npx pnpm@9.15.9 build
Set-Location ..
gitleaks detect --source . --config .gitleaks.toml --no-git --redact
git diff --check
```

Confirm that `.env`, `.run/`, generated databases, sanitized snapshots, `frontend/dist`, `frontend/node_modules`, `.venv`, logs, raw/debug data, and local-only specs remain untracked.

## Safe Troubleshooting

- If startup reports an occupied port, stop the known process yourself or choose the correct existing development session. The supervisor will not kill it.
- If status reports an unvalidated process, the supervisor will not stop it.
- If Brief Suggestions are not configured, set the source in local `.env`; no path is returned in the API error.
- Use the individual development commands when interactive logs are needed. Do not add persistent raw logging.
