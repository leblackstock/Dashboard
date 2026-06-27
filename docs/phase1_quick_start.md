# Phase 1 Quick Start

1. Install backend dependencies: `task backend:sync`
2. Initialize SQLite: `task db:init`
3. Run the collector manually: `task collector:codex`
4. Start the API: `task backend:dev`
5. Install frontend dependencies: `task frontend:install`
6. Start the frontend: `task frontend:dev`
7. Verify the API at `GET /api/ai/codex/live-usage`
8. Verify the frontend displays the Codex Usage card

Generated SQLite files and sanitized snapshots are local-only by default. Only `data/sanitized/codex/.gitkeep` is expected in source control.
