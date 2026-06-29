# Phase 2 Implementation Plan

Current master spec: `dashboard_master_spec_v4.52.md`

Phase 1 is complete, pushed, and tagged at `phase1-codex-usage-v0.1.0`.

Published Phase 1 checkpoint:

- Repo: `https://github.com/leblackstock/Dashboard`
- Branch: `main`
- Tag: `phase1-codex-usage-v0.1.0`
- Commit: `f377a6937cb9f781700c74bf024f302f292fb1e4`

Do not start Phase 2 coding until this plan is approved.

Before coding, make the repo docs reflect v4.46 as the current approved master spec.

## A. Phase 2 Scope

Target: `Daily Command Center v1`.

Build one useful Daily dashboard view with the locked Phase 2 card order:

1. Codex Usage
2. Today’s Top 3
3. Active Projects
4. Blocked / Needs Review
5. Quick Capture
6. Collector Health

In scope:

- Daily dashboard shell.
- Existing Codex Usage card carried forward.
- Today’s Top 3 card.
- Active Projects card.
- Blocked / Needs Review card.
- Quick Capture card.
- Collector Health card.
- Project Registry v1.
- Basic dark/glow frontend polish.

Locked defaults:

- Project registry starts as SQLite tables only.
- Daily layout starts as a fixed card layout.
- Today’s Top 3 is manual first and keeps project optional.
- Today’s Top 3 shows all non-completed items.
- Today’s Top 3 also shows items completed today, collapsed/faded.
- Today’s Top 3 hides items completed before today by default.
- Today’s Top 3 does not add calendar/recurrence behavior in Phase 2.
- Project/task cards are manual first.
- Quick Capture saves user-entered local note/capture text and classifies later.
- Quick Capture must not ingest raw logs, raw endpoint payloads, prompt history, auth files, rollout files, or pasted secret dumps.
- No AI auto-classification in Phase 2 unless explicitly approved.
- Keep the Codex collector manual unless scheduled collection is explicitly approved.
- Do not add new provider collectors in Phase 2.
- UI starts clean/simple with dark mode and purple/violet/cobalt glow direction.
- Phase 2 stops when the Daily dashboard is useful.

Out of scope:

- Best AI Tool recommendation engine.
- AI usefulness/output-quality scoring UI.
- Claude collectors.
- ChatGPT collectors.
- Scheduled collectors.
- Draggable/resizable grid.
- Weekly/Monthly pages.
- Notifications.
- Calendar/email integrations.
- External hosting.
- Multi-user auth.
- MCP/token proxy/autonomous memory.

## B. Schema/Database Changes

Add Phase 2 tables in SQLite using `backend/db/schema.sql`.

`projects`:

- `project_key`
- `project_label`
- `parent_project_key`
- `status`
- `priority`
- `default_ai_tool`
- `safe_notes`
- `created_at`
- `updated_at`

Allowed project statuses:

- `Active`
- `Paused`
- `Someday`
- `Archived`
- `Blocked`
- `Needs Review`

Initial project groups:

- Dashboard / LifeOps Command Center
- AI Tools / Usage
- Drakkar Designs
- Woodworking / CNC
- Social Media / Marketing
- Finance / Admin
- Books Projects
- WoW / Gaming
- Home / Tech
- Other / Unsorted

`daily_top_items`:

- `id`
- `title`
- `project_key`
- `reason`
- `status`
- `sort_order`
- `pinned`
- `created_at`
- `updated_at`
- `completed_at`

`quick_captures`:

- `id`
- `text`
- `captured_at`
- `project_key`
- `capture_type`
- `status`
- `processed`
- `created_at`
- `updated_at`

`blocked_items`:

- `id`
- `project_key`
- `title`
- `reason`
- `status`
- `next_action`
- `created_at`
- `updated_at`
- `resolved_at`

Collector Health should read existing `collector_runs` first. Extend that table only if the current Phase 1 shape cannot safely provide last success, last failure, latest status, records written, safe error message, and freshness metadata.

Do not add Codex historical aggregate tables in Phase 2 unless explicitly approved later.

## C. API Endpoints

Keep existing Phase 1 endpoints:

- `GET /api/health`
- `GET /api/ai/codex/live-usage`

Add sanitized local endpoints:

- `GET /api/daily`
- `GET /api/projects`
- `POST /api/projects`
- `PATCH /api/projects/{project_key}`
- `GET /api/top-items`
- `POST /api/top-items`
- `PATCH /api/top-items/{item_id}`
- `GET /api/blocked-items`
- `POST /api/blocked-items`
- `PATCH /api/blocked-items/{item_id}`
- `GET /api/quick-captures`
- `POST /api/quick-captures`
- `PATCH /api/quick-captures/{capture_id}`
- `GET /api/collectors/health`

Endpoint rules:

- Responses return only approved local/sanitized fields.
- Project keys stay stable and reusable for Phase 3.
- `GET /api/daily` aggregates the card data needed for the Daily dashboard without exposing raw collector data.
- Quick Capture accepts local user-entered note/capture text only; it must not become an import path for raw logs, raw endpoint payloads, prompt history, auth files, rollout files, or pasted secret dumps.

## D. Frontend Components/Cards

Create or update:

- `DailyDashboard`
- `DashboardCard`
- `CodexUsageCard`
- `TodaysTop3Card`
- `ActiveProjectsCard`
- `BlockedReviewCard`
- `QuickCaptureCard`
- `CollectorHealthCard`
- shared status/freshness badges
- shared empty/loading/error states
- minimal shared form controls where they match existing frontend patterns

Frontend rules:

- Fixed layout only.
- No drag or resize behavior.
- Desktop-first, responsive enough for normal local use.
- Dark mode with restrained purple/violet/cobalt glow.
- Clear stale/fresh/confidence badges.
- No visible raw secrets, raw logs, prompt previews, full workspace paths, or raw collector payloads.

## E. Implementation Slices

1. Repo/doc alignment
   - Make v4.46 the active repo spec.
   - Add or update the docs copy of the v4.46 spec.
   - Update `AGENTS.md`, `docs/handoff.md`, `docs/decisions.md`, and `docs/runbook.md` only as needed.
   - Keep the Phase 1 tag untouched.

2. Schema foundation
   - Add Phase 2 SQLite tables.
   - Seed initial project groups only if the existing DB init pattern supports safe, idempotent seed data.
   - Add schema tests.

3. Backend routes and models
   - Add project registry CRUD.
   - Add Today’s Top 3 CRUD.
   - Add blocked/needs-review CRUD.
   - Add Quick Capture create/list/update.
   - Add Collector Health summary from existing collector run data.
   - Add Daily aggregate endpoint.

4. Frontend shell
   - Convert the current single-card app into the Daily dashboard shell.
   - Carry forward the existing Codex Usage card without weakening Phase 1 behavior.

5. Frontend cards
   - Implement manual-first Top 3.
   - Implement Active Projects from the registry.
   - Implement Blocked / Needs Review.
   - Implement Quick Capture.
   - Implement Collector Health.

6. Polish and acceptance
   - Add basic dark/glow styling.
   - Add freshness/status badges.
   - Run backend tests, lint, frontend build, secret scan, and gitignore checks.

## F. Tests And Safety Checks

Backend tests:

- Schema initialization is idempotent.
- Project registry endpoints validate required fields and allowed statuses.
- Today’s Top 3 returns all non-completed items.
- Today’s Top 3 returns items completed today with collapsed/faded metadata.
- Today’s Top 3 hides items completed before today by default.
- Today’s Top 3 adds no calendar or recurrence behavior.
- Quick Capture stores and returns only local capture fields.
- Blocked / Needs Review rows can be created, updated, resolved, and listed.
- Collector Health returns safe summary data from collector runs.
- Daily aggregate endpoint returns the expected card shape.
- Existing Codex Usage endpoint still passes Phase 1 tests.

Frontend checks:

- TypeScript build passes.
- Cards render loading, empty, error, and populated states.
- Manual forms submit and refresh local data.
- Codex Usage card still renders correctly in the new shell.
- Layout remains fixed and usable without drag/resize behavior.

Security checks:

- Run `uv run pytest`.
- Run `uv run ruff check .`.
- Run the frontend build through the existing frontend command.
- Run the repo’s Gitleaks/redacted secret scan command.
- Confirm generated/local artifacts remain gitignored.
- Confirm tracked files do not contain access tokens, refresh tokens, cookies, authorization headers, auth file contents, raw endpoint payloads, prompt previews, first user messages, raw logs, raw rollout files, or full workspace paths by default.

## G. Files Expected To Create/Modify

Expected backend changes:

- `backend/db/schema.sql`
- `backend/app/models.py`
- `backend/app/main.py`
- `backend/app/db.py`
- `backend/app/routes/daily.py`
- `backend/app/routes/projects.py`
- `backend/app/routes/top_items.py`
- `backend/app/routes/blocked_items.py`
- `backend/app/routes/quick_captures.py`
- `backend/app/routes/collector_health.py`
- `backend/tests/test_phase2_schema.py`
- `backend/tests/test_projects_route.py`
- `backend/tests/test_top_items_route.py`
- `backend/tests/test_blocked_items_route.py`
- `backend/tests/test_quick_captures_route.py`
- `backend/tests/test_collector_health_route.py`
- `backend/tests/test_daily_route.py`

Expected frontend changes:

- `frontend/src/App.tsx`
- `frontend/src/components/CodexUsageCard.tsx`
- `frontend/src/components/DailyDashboard.tsx`
- `frontend/src/components/DashboardCard.tsx`
- `frontend/src/components/TodaysTop3Card.tsx`
- `frontend/src/components/ActiveProjectsCard.tsx`
- `frontend/src/components/BlockedReviewCard.tsx`
- `frontend/src/components/QuickCaptureCard.tsx`
- `frontend/src/components/CollectorHealthCard.tsx`
- `frontend/src/lib/api.ts`
- `frontend/src/lib/types.ts`
- `frontend/src/styles.css`

Expected docs/config changes:

- `AGENTS.md`
- `docs/dashboard_master_spec_v4.52.md`
- `docs/handoff.md`
- `docs/decisions.md`
- `docs/runbook.md`
- `docs/phase2_implementation_plan.md`

Do not modify package managers, add new services, or add new major frameworks as part of Phase 2 without explicit approval.

## H. Package/Tool Changes Needing Approval

No package or tool changes are expected.

Use the existing approved stack:

- `uv` for Python dependency/project management.
- FastAPI backend.
- SQLite database.
- React + Vite + TypeScript frontend.
- Tailwind + shadcn/ui styling.
- Existing `Taskfile.yml` commands.
- Existing Gitleaks/redacted secret scan workflow.

Stop and ask before adding any new major package, framework, service, template, MCP tool, scheduler, auth system, database, external integration, provider collector, or autonomous memory feature.

## I. Open Questions Before Coding

Required approval:

- Approve this v4.46 Phase 2 plan before coding begins.

Recommended confirmations:

- Confirm the first Phase 2 coding step should be repo/doc alignment: make v4.46 the active repo spec.
- Confirm Codex historical aggregates are deferred unless explicitly approved later.
- Confirm no scheduler/background collector should be added in Phase 2.
- Confirm fixed layout first, with draggable/resizable grid deferred.
