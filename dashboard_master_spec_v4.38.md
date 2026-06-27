# Dashboard Master Spec v4.38

Created: 2026-06-26
Previous version: v4.37

## Core Concept

A personal LifeOps / project command-center dashboard that shows the most important status, priorities, metrics, and activity across everything Lauren is working on.

The dashboard should act as a central hub with:
- Main overview page
- Links to individual project pages
- High-level summaries from each active area
- Priority and 80/20 decision support
- AI usage tracking
- AI subscription limit/reset tracking
- Script-fed metrics from repos and external exports
- Automation-first data collection
- Visible data confidence and staleness indicators
- Draggable/reorderable dashboard cards
- Daily / Weekly / Monthly top navigation
- Icon-based left project navigation

## Locked Decisions

### App Type

- Responsive web dashboard
- Local-first
- PWA-capable later
- Designed for both desktop and phone

### Phone Access

- Tailscale first
- Private access from phone to local dashboard
- Avoid public hosting at the start unless needed later

### Data Entry Philosophy

Lauren strongly prefers avoiding manual data entry whenever possible.

The dashboard should be designed as:

```txt
automation-first
script/import-driven
manual-entry-last-resort
```

Manual entry should exist only for:
- Quick corrections
- Missing data that cannot be fetched/imported
- One-off notes
- Emergency override/status changes
- Temporary stopgap before automation exists

The app should never rely on manual entry as the main workflow if there is a realistic way to automate, import, scrape, parse, or infer the data.

### Data Visibility Philosophy

Do not hide uncertain or stale data by default.

Instead, show it with clear confidence and freshness indicators.

The dashboard should make it obvious when data is:
- fresh
- slightly stale
- stale
- very stale
- automatic
- imported
- inferred
- manually corrected
- unknown

The goal is to avoid false confidence while still keeping useful last-known information visible.

### Freshness Warning Rules

Freshness warning rules should vary by source type, with sensible initial defaults set by Codex.

Recommended initial thresholds:

| Source Type | Fresh | Slightly Stale | Stale / Warning | Very Stale |
|---|---:|---:|---:|---:|
| AI subscription limits | under 2 hours | 2-6 hours | over 6 hours | over 24 hours |
| Repo activity scans | under 24 hours | 1-2 days | over 2 days | over 7 days |
| Time/project activity | under 24 hours | 1-2 days | over 2 days | over 7 days |
| Meta insights | under 24 hours | 1-3 days | over 3 days | over 7 days |
| Wheelhouse/Airbnb metrics | under 24 hours | 1-3 days | over 3 days | over 7 days |
| Weekly review metrics | current week | 1 week old | over 1 week | over 1 month |
| Monthly/billing data | current month | 1 month old | over 1 month | over 3 months |

AI limits should warn faster because they affect immediate tool availability. Weekly/monthly metrics can tolerate slower freshness windows.

Codex may adjust these thresholds later if real-world behavior shows a better cadence.

### Data Architecture

Use a hybrid data approach:

```txt
Repo scans
+ scheduled scripts
+ JSON imports
+ Markdown/project files
+ optional manual corrections
        ↓
SQLite database
        ↓
Dashboard UI
```

### Storage Roles

- Markdown: human-readable project pages, notes, decisions, context
- JSON: script output/import files
- SQLite: dashboard database for searching, filtering, charts, history, and trends

The user does not need to manually work with SQL at the beginning.

## Data Sources

Initial data sources should include:

- GitHub/local repos
- Automated repo activity scans
- AI usage tracking
  - ChatGPT
  - Codex
  - Claude
  - Claude Cowork
  - Claude Design
  - Other AI tools later
- AI subscription/limit tracking
- Scheduled or manually run scripts for:
  - Meta insights
  - Wheelhouse/Airbnb metrics
  - repo/project activity
  - time spent
  - priority/80-20 review
- Manual entries only as fallback/correction

There are currently no direct app integrations planned. Data should come from repos, scripts, local scans, exports, imports, and manual fallback fields where unavoidable.

## Dashboard Navigation System

The dashboard should use a two-level navigation model:

```txt
Top navigation: Daily / Weekly / Monthly
Left navigation: Project views using icons
Main area: Draggable + grid-resizable cards
```

### Top Timeframe Navigation

The top of the dashboard should include timeframe options:

- Daily
- Weekly
- Monthly

These should change the dashboard’s focus and metrics:

- Daily: today’s priorities, current blockers, available AI tools, urgent project activity
- Weekly: trends, time allocation, progress, automation/script results, review items
- Monthly: subscription value, billing, bigger project progress, long-term metrics

Future timeframe options may include:
- Quarterly
- Custom range
- Review mode

### Left Project Navigation

The left side should show specific project views.

Lauren prefers icons instead of long project names when possible.

Project nav should support:
- Custom icon per project
- Tooltip or label on hover/tap
- Short label option
- Reorderable project icons
- Pinned/favorite projects
- Collapsible project groups
- Status indicators
  - active
  - blocked
  - stale
  - needs review
- Small badges for urgent counts or stale data

Example project nav icons:

```txt
Dashboard / LifeOps     → command icon
AI Tools / Usage        → spark/brain icon
Drakkar Designs         → shield/wood/brand icon
Airbnb / Wheelhouse     → house icon
Finance / Admin         → coin/calculator icon
Moola-Matic             → money/automation icon
Books Projects          → book icon
WoW / Gaming            → sword/controller icon
Home / Tech             → wrench/house icon
Personal / Misc         → star/user icon
Other / Unsorted        → inbox/archive icon
```

### Customization Goal

Lauren is okay with phased implementation, but the long-term goal must remain clear:

```txt
Final goal: make dashboard navigation, layout, project icons, card order, card size, groups, and major settings customizable/reorderable wherever practical.
```

V1 may keep some pieces fixed for simplicity, but the architecture should not block deeper customization later.

Recommended phased approach:

1. V1:
   - Fixed Daily / Weekly / Monthly tabs
   - Reorderable project icons
   - Draggable + grid-resizable dashboard cards
   - Saved layout
   - Hide/show cards
2. V2:
   - Reorderable project groups
   - More icon customization
   - Separate desktop/phone layout editing
   - Custom default landing view
3. V3:
   - Reorderable/custom timeframe tabs
   - Custom views
   - Saved layout presets
   - More advanced settings and personalization

### Reorderable Settings

The dashboard should make these reorderable/customizable where practical:

- Top timeframe tabs
- Left project nav items
- Project groups
- Dashboard cards
- Card sizes
- Pinned projects
- Hidden/collapsed cards
- Default view
- Per-device layout preferences

### Navigation Settings UI

Settings should include:

- Reorder project icons
- Pick/change project icon
- Rename short label
- Pin/unpin project
- Hide/show project from left nav
- Choose default landing view
- Reset layout/navigation to defaults
- Manage desktop vs phone layout if needed

## Dashboard Layout Customization

Dashboard cards/widgets should be draggable and resizable by grid units.

Lauren wants to move cards as needed, so the dashboard should not be a fixed rigid layout.

### Requirements

- Cards should be draggable/reorderable on desktop.
- Cards should be resizable by grid units, not freeform pixel sizing.
- Mobile layout should support a simpler reorder/size mode if drag-and-drop is awkward.
- Layout changes should persist.
- Layout should support different views where practical:
  - Desktop layout
  - Phone layout
  - Possibly future tablet layout
- Cards should be hideable/collapsible.
- Pinned cards should stay near the top unless manually moved.
- The system should provide a reset-to-default layout option.
- The layout engine should avoid breaking the visual style when cards are moved or resized.
- Grid snapping should keep spacing consistent and prevent chaotic layouts.

### Card Sizing Rules

Cards should use grid units such as:

- Small: 1 × 1
- Medium: 2 × 1
- Large: 2 × 2
- Wide: 3 × 1
- Hero: 4 × 2

Each card/widget should define:
- Minimum width/height
- Default width/height
- Maximum width/height where needed
- Whether it can be resized
- Whether it can be hidden/collapsed
- Preferred desktop size
- Preferred mobile size/order

Important status cards should have sensible minimum sizes so key labels, confidence badges, and reset countdowns remain readable.

### Suggested Implementation Direction

Use a responsive dashboard grid with saved layout state, draggable cards, and grid-based resizing.

Possible implementation options:
- React Grid Layout or similar grid-based dashboard layout library
- CSS grid plus custom reorder/resize controls only if simpler
- Separate mobile ordering/sizing rules for phone
- Store layout preferences in SQLite/local settings

The first version should support draggable + grid-resizable cards if practical. If implementation gets too complex, fallback should be draggable ordering first with grid resizing as the immediate next milestone.

## Daily View

The Daily view is the default fast-decision command center.

It should answer:

- What matters most today?
- What is blocked?
- Which AI tools are available right now?
- What should Lauren work on first?
- What changed recently?
- Is any important data stale or broken?

### Daily View v1 Cards

Suggested v1 Daily cards:

1. Today’s Top 3
2. Best AI Tool to Use Right Now
3. AI Limits / Reset Countdowns
4. Active Projects
5. Blocked / Needs Attention
6. 80/20 Focus
7. Recent Repo Activity
8. Automation Health
9. Quick Capture
10. Time Allocation Today

### Quick Capture

Quick Capture should accept anything first, then sort/classify later.

Recommended v1 behavior:

- One fast input box
- Accept tasks, notes, ideas, reminders, project thoughts, links, blockers, and random brain dumps
- Dashboard/AI-assisted classifier suggests:
  - project
  - type
  - priority
  - urgency
  - next action
  - whether it belongs in Today’s Top 3
- Lauren can correct classification only when needed
- Do not force structured entry up front

This matches the automation-first philosophy and avoids turning capture into homework.

### Today’s Top 3

The “Today’s Top 3” card should be both:

- Auto-suggested by the dashboard
- Manually overrideable/pinnable by Lauren

The dashboard should suggest Top 3 items based on:

- Project priority
- Urgency/deadlines
- Blockers
- Recent activity
- Stale or broken automation/data
- 80/20 impact
- AI tool availability
- Manually pinned items

Lauren should be able to override the suggestions and lock/pin her own Top 3 when needed.

The card should show why each item was suggested.

Example:

```txt
1. Check Codex limit reset
Reason: Codex is near limit and Dashboard Build is active today.

2. Fix Drakkar product image workflow
Reason: High impact project, recent activity, blocks listing progress.

3. Review Finance/Admin deadline
Reason: High urgency and stale status.
```

## Main Dashboard Modules

The home dashboard should include:

- Daily / Weekly / Monthly timeframe tabs
- Icon-based left project navigation
- Draggable/customizable card layout
- Today’s Top 3 with auto-suggest + manual override
- Today’s Command Center
- Top priorities
- Urgent blockers
- Active project cards
- Project registry/search/filter access
- 80/20 focus panel
- Time spent by project
- AI usage by tool
- AI subscription limit status
- AI reset countdowns
- AI tool availability recommendations
- AI recommendation reason/explanation
- Recent project activity
- Quick capture box
- Links to each project page
- Weekly/daily script results
- High-level metric snapshots from major work areas
- Automation health/status panel showing whether scripts last ran successfully
- Data confidence/staleness summary

## Main Project Categories

The first detailed category being planned is:

- AI Tools / Usage

Initial project registry structure:

- Dashboard / LifeOps Command Center
- AI Tools / Usage
- Drakkar Designs
  - Woodworking Projects
  - CNC / Woodworking Production
  - Cedar Garden/Decor Products
  - Social Media / Marketing
  - Meta Insights
  - Product Images / Marketplace Graphics
- Airbnb / Wheelhouse
- Finance / Admin
- Moola-Matic
- Books Projects
- WoW / Gaming
- Home / Tech
- Personal / Misc
- Other / Unsorted

Important: Drakkar Designs is an umbrella project. Wavy flags, CNC production, cedar products, social/marketing, Meta insights, and product graphics should be subprojects or workstreams under Drakkar, not separate top-level projects.

The system should support adding more projects later because some projects are currently forgotten/unknown.

## Data Confidence and Staleness System

### Purpose

The dashboard should show useful last-known data without pretending it is perfect.

Uncertain data should be visible but clearly labeled.

### Confidence Levels

Suggested confidence labels:

- High confidence
  - automatic source
  - recent successful fetch/import
  - clear structured data
- Medium confidence
  - imported or parsed successfully
  - possible minor ambiguity
  - data is recent enough but not live
- Low confidence
  - inferred from partial data
  - screenshot/HTML parsed
  - manual correction
  - source behavior is uncertain
- Unknown confidence
  - no reliable source
  - never checked
  - old placeholder/sample data

### Freshness Labels

Suggested freshness labels:

- Live / just updated
- Fresh
- Slightly stale
- Stale
- Very stale
- Never checked
- Sample data

### Visual Treatment

Each important metric/card should be able to show:

- Source badge
- Last checked timestamp
- Confidence badge
- Freshness badge
- Warning icon when stale
- Tooltip explaining where the data came from
- Small “rerun check” action where practical

### Example Status Labels

```txt
ChatGPT limit: Available
Confidence: Medium
Freshness: Slightly stale
Last checked: 2h ago
Source: Browser-assisted scrape
```

```txt
Wheelhouse revenue: $___
Confidence: High
Freshness: Fresh
Last checked: Today 8:00 AM
Source: Scheduled import
```

```txt
Claude remaining usage: Unknown
Confidence: Unknown
Freshness: Never checked
Source: Not configured
```

## AI Tools / Usage Section

### Purpose

Track whether AI tools are actually helping, where time/money/subscription capacity is going, and which tools are most useful for each project.

### Current Usage Reality

Most AI usage is currently subscription-based rather than API-based.

Therefore, the AI section should prioritize subscription limit tracking first. API token/cost tracking should still exist, but as a secondary/future-friendly layer.

### Tools to Track

First-version AI subscription tools:
- ChatGPT
- Codex
- Claude
- Claude Cowork
- Claude Design

Other tools can be added later.

### First-Version AI Tool Priority

The first version should focus on tracking the subscription limits, reset windows, usage status, usefulness, and project association for:

1. ChatGPT
2. Codex
3. Claude
4. Claude Cowork
5. Claude Design

### V1 AI Dashboard Priority

V1 should track both:
- Availability / limits
- Usefulness / value

However, availability and limits should get the main dashboard space because they affect immediate tool choice.

The dashboard should answer these questions quickly:
- Which AI tools are available right now?
- Which tools are near their limits?
- Which tools are exhausted?
- When does each tool reset?
- Which tool should Lauren use next based on available capacity?
- Which subscriptions are actually proving useful over time?

Usefulness/value should still be tracked, but it can live in supporting cards, detail views, and weekly/monthly review panels rather than dominating the home dashboard.

### Best AI Tool Recommendation Logic

The “best AI tool to use right now” recommendation should be project-first.

Lauren prefers AI usage and recommendations to be sorted primarily by project, not generic task type.

The recommendation should use a combination of:

1. Available capacity / current limits
2. Best tool for the current project
3. Historical usefulness/value score for that project
4. Optional task-type fit as a secondary tag only

Availability alone should not determine the recommendation.

Example logic:

```txt
recommended_tool_score =
  availability_score * 0.35
+ project_fit_score * 0.35
+ project_usefulness_score * 0.20
+ task_type_fit_score * 0.10
```

This weighting can be adjusted later after real usage data exists.

The dashboard should show the reason for each recommendation, not just the answer.

Example:

```txt
Project: Dashboard Build
Recommended: Codex
Reason: Strongest project fit, available capacity is high, and previous dashboard-related Codex sessions were useful.
```

If the best-fit tool for a project is near/exhausted, the dashboard should recommend the best available alternative.

Example:

```txt
Project: Drakkar Product Images
Best fit: Claude Design
Status: exhausted until 8:00 PM
Recommended fallback: ChatGPT
Reason: Available now and historically useful for prompt cleanup on this project.
```

Task type can still exist, but only as a secondary label used inside project context.

Example secondary task labels:
- coding
- debugging
- planning
- writing
- design prompting
- research
- automation/scripting
- marketing
- long-form spec work
- quick answer

### Locked Tracking Priorities

The AI usage section should track all of the following:

- Subscription plan/tool
- Usage limits
- Remaining capacity
- When limits are exhausted
- Reset time/date/countdown
- Cost / credits / tokens when available
- Time spent
- Which project the AI helped
- Which AI tool was used
- Whether the output was actually useful
- Data confidence/staleness for each usage/limit metric

## AI Usage Research Findings

Online research shows that “real token usage” dashboards generally come from one of three source types:

1. Official API usage/cost systems
2. Local coding-agent logs
3. Observability/proxy tools that sit between the app and the model provider

This is different from normal consumer subscription chat usage, where exact token-level details may not always be exposed.

### OpenAI API Usage

OpenAI API usage can be tracked through:
- API Usage Dashboard
- CSV exports for usage/cost
- Usage API / Costs endpoint for programmatic token/cost tracking

This is best for API-based usage, not necessarily ordinary ChatGPT subscription chats.

### OpenAI ChatGPT / Codex Subscription Usage

ChatGPT/Codex subscription visibility is different from API usage visibility.

Known useful surfaces:
- Codex usage dashboard
- Codex CLI `/status`
- ChatGPT/Enterprise/Edu analytics where eligible
- Usage/credit analytics for Business/Enterprise/Edu workspaces

For personal ChatGPT subscription usage, exact token-level export may not be available in the same way API usage is. The dashboard should track availability, limits, reset messages, credits, and visible usage status first.

### Anthropic / Claude API Usage

Anthropic has official Usage and Cost APIs for Claude Platform organizations. These can track token consumption, costs, model/workspace/service-tier breakdowns, and usage buckets.

Important limitation:
- Anthropic states the Usage & Cost Admin API is unavailable for individual accounts.
- Enterprise/Team-style analytics may expose more data depending on plan/admin access.

### Claude Code Local Usage Logs

Community dashboards show that Claude Code writes local JSONL session logs containing detailed usage data such as token counts, models, sessions, projects, and cache/token breakdowns.

This is very important for Lauren’s dashboard because it may allow local, automation-first token tracking for Claude Code/Cowork-like coding usage without manual entry.

Candidate local log sources to investigate:
- `~/.claude/projects/*/*.jsonl`
- Any Claude Code / Claude desktop / IDE integration local history files
- CLI command output such as `/usage` where available

The dashboard should parse local logs where allowed and safe, then normalize them into the same AI usage schema.

### Observability Tools

Tools such as Langfuse, Helicone, LiteLLM, LangSmith, Portkey, Vantage, Grafana, Datadog, and similar systems can track token usage and costs when AI calls pass through an API, SDK, proxy, or gateway.

These are useful if Lauren later builds scripts/agents that call APIs directly. They are less useful for normal subscription web UI usage unless the product exposes logs or exports.

### Important Design Decision

The dashboard must support multiple AI usage source types:

```txt
API token usage
+ subscription capacity/limits
+ local agent logs
+ usage dashboard exports
+ browser/CLI visible status
+ manual correction fallback
```

Do not assume one universal tracking method works for every AI tool.

### Source Reliability Ranking

Recommended reliability ranking:

1. Official API usage endpoint/export
2. Official local agent logs with token fields
3. Official usage dashboard CSV/export
4. Official CLI command output
5. Official usage page scrape/screenshot
6. Community-derived local parser
7. Inferred from visible limit/reset banners
8. Manual correction fallback

### Updated AI Collector Priority

V1 collector priority should be:

1. Claude Code / Claude-family local logs, if present
2. Codex VS Code `agentSessions.model.cache` for session/activity tracking
3. Codex VS Code usage dropdown/state or usage dashboard for availability/limits; CLI `/status` only if installed later
3. ChatGPT visible limits/credits/reset info
4. Anthropic/OpenAI API usage endpoints only if Lauren is using API keys
5. Optional observability integration later if scripts/agents start using APIs heavily

## AI Usage Acquisition Process

This section defines how the dashboard should obtain AI usage, limits, availability, reset times, and subscription value signals while minimizing manual entry.

### Core Principle

AI usage collection should be automation-first and source-aware.

Preferred acquisition order:

1. Official API or official usage endpoint/export if available
2. Official usage/settings page captured locally while Lauren is logged in
3. Official CLI/desktop command output where available
4. Browser-assisted snapshot or screenshot/HTML capture parsed locally
5. Manual correction only as a fallback

Do not design the dashboard around manual usage entry.

### Safety / Account Handling

The dashboard should avoid storing account passwords.

Preferred safety rules:

- User logs in through the normal browser/app when needed
- Scripts collect from already-visible local pages, exports, or CLI output
- Store only structured usage data, timestamps, and source metadata
- Never store raw tokens, cookies, authorization headers, or auth file contents.
- Make collection user-triggered first, then scheduled only where safe
- Respect provider terms and avoid abusive automated extraction

### Tool-Specific Source Strategy

#### ChatGPT

Likely sources:
- Official settings, usage, and model-limit pages while Lauren is logged in
- Official exports or documented usage endpoints if available
- Local browser-assisted capture only when official structured data is unavailable
- Manual correction as fallback

Useful normalized fields:
- provider/tool
- account key hash and local display label
- plan/subscription type
- model/tool availability
- reset time/window if shown
- percent used/remaining when available
- source label, confidence, freshness, and last checked timestamp

#### Codex

Durable confirmed sources:
- Live Codex quota snapshots come from the sanitized `/wham/usage` collector.
- Local Codex SQLite data can support historical session, token, model, project-label, daily, and weekly trend charts.
- Codex doctor/config output is useful for health/config/runtime status only, not live quota values.
- VS Code state/log locations may help discovery, but raw logs, prompt text, rollout files, and full workspace paths must not be ingested by default.

Live quota source:
- Endpoint:
  `https://chatgpt.com/backend-api/wham/usage`
- Auth source:
  existing local Codex auth, read safely and never printed.
- Polling:
  no faster than once per minute.
- Normalized windows:
  - 300-minute primary window = Codex 5-hour quota window
  - 10,080-minute secondary window = Codex weekly quota window

Confirmed Codex live quota fields:
- `plan_type`
- `reset_credits_available`
- `quota_5h_used_percent`
- `quota_5h_remaining_percent`
- `quota_5h_reset_at`
- `quota_weekly_used_percent`
- `quota_weekly_remaining_percent`
- `quota_weekly_reset_at`

Historical Codex fields/charts:
- provider/tool/model
- provider-neutral `session_count`
- token trend by day/week/month
- session trend by day/week/month
- safe project label/project key hash
- model/reasoning-effort breakdown where available

Safety:
- Never store raw access tokens, refresh tokens, cookies, authorization headers, or auth file contents.
- Store safe project labels by default.
- Raw workspace paths are local-only opt-in.
- Do not expose prompt previews, first user messages, raw logs, raw rollout files, or full workspace paths by default.

#### Claude / Claude Code / Claude Cowork / Claude Design

Likely sources:
- official account, subscription, usage, and settings pages where available
- local Claude Code logs/config/state if safe structured usage data is available
- exports or APIs where available
- manual correction as fallback

Open investigation:
- Verify exact local Claude Code log/source structure.
- Confirm how Claude Cowork and Claude Design should map to tracked tools.
- Confirm non-Codex subscription plans, reset rules, and usage windows.

### Collector Architecture

Use one collector per provider/tool family.

Suggested structure:

```txt
scripts/
  collectors/
    ai/
      openai_chatgpt_usage/
      openai_codex_usage/
      openai_codex_vscode_extension_discovery/
      anthropic_claude_usage/
      anthropic_claude_code_usage/
      local_agent_log_parsers/
      api_usage_imports/
      normalize_ai_usage.py
```

Each collector should output JSON into:

```txt
data/imports/ai/
  chatgpt_usage_snapshot.json
  codex_usage_snapshot.json
  codex_local_sources_inventory.json
  codex_vscode_usage_snapshot.json
  codex_vscode_sessions_snapshot.json
  codex_doctor_health_snapshot.json
  codex_sqlite_schema_inventory.json
  codex_thread_token_aggregate_snapshot.json
  codex_log_health_aggregate_snapshot.json
  claude_usage_snapshot.json
  claude_code_usage_snapshot.json
  local_agent_log_usage_snapshot.json
  api_usage_snapshot.json
  ai_usage_normalized.json
```

### Normalized AI Usage Snapshot Schema

```json
{
  "provider": "openai",
  "tool": "codex",
  "display_name": "Codex",
  "account_label": "primary",
  "account_key_hash": null,
  "account_name": null,
  "plan": "unknown",
  "status": "available",
  "limit_type": "subscription_usage",
  "limit_window": "5h_or_weekly",
  "used_amount": null,
  "remaining_amount": null,
  "percent_used": null,
  "reset_at": null,
  "reset_countdown": null,
  "credit_balance": null,
  "reset_credits_available": null,
  "quota_5h_used_percent": null,
  "quota_5h_remaining_percent": null,
  "quota_5h_reset_at": null,
  "quota_weekly_used_percent": null,
  "quota_weekly_remaining_percent": null,
  "quota_weekly_reset_at": null,
  "recent_usage": null,
  "input_tokens": null,
  "output_tokens": null,
  "cache_read_tokens": null,
  "cache_write_tokens": null,
  "model": null,
  "session_count": 1,
  "session_id": null,
  "project_label": null,
  "project_key_hash": null,
  "raw_project_path": null,
  "source_type": "official_usage_page_or_local_log",
  "source_label": "Codex Settings > Usage Dashboard",
  "collected_at": "2026-06-26T00:00:00-04:00",
  "confidence": "medium",
  "freshness": "fresh",
  "notes": "Use last-known value with warning if stale."
}
```

Schema notes:
- Canonical account grouping field: `account_key_hash`.
- `account_label` and `account_name` are local display fields.
- Use `project_label` and `project_key_hash` by default.
- `raw_project_path` is local-only opt-in and should not appear in normal exports.
- Codex quota fields may be null for non-Codex providers or when unavailable.

### Confidence Rules

Suggested confidence by acquisition method:

- Official API/export: high
- Official usage page parsed successfully: medium/high
- CLI/IDE command output: medium/high
- Screenshot/HTML parse: medium
- Inferred from banners/notifications: low/medium
- Manual correction: low/medium depending on timestamp
- Never checked/sample data: unknown

### Scheduling

Suggested starting schedule:

- AI limit checks: every 1-2 hours while dashboard machine is awake
- Repo scans: daily
- Meta insights: daily
- Wheelhouse/Airbnb metrics: daily or every few days
- Weekly review metrics: weekly
- Monthly subscription value review: monthly

AI limits should have faster freshness warnings because they affect immediate tool choice.

### UI Requirements

The AI Usage / Limits area should show:

- Available now
- Near limit
- Exhausted until reset
- Reset countdown
- Credit balance where applicable
- Last checked
- Source type
- Confidence badge
- Freshness badge
- Rerun/check button
- “Best AI tool to use right now” recommendation
- “Why this recommendation?” explanation

### Implementation Phases

#### Phase 1: Mock + manual seed data

- Build UI with realistic sample data
- Define normalized schema
- Add confidence/freshness badges
- Add manual correction fields only as fallback

#### Phase 2: Local collector prototypes

- Build collectors for local agent logs, visible official usage pages, and CLI output
- User-triggered first
- Output JSON snapshots
- Import snapshots into SQLite

#### Phase 3: Scheduled checks

- Add scheduled local runs
- Add automation health card
- Add stale/error warnings

#### Phase 4: Smarter recommendations

- Use availability + project fit + historical usefulness
- Add fallback recommendations when best-fit tool is exhausted
- Track subscription value over weekly/monthly periods

## AI Subscription Limit Tracking

### Purpose

Help Lauren know which AI tools are available right now, which are close to limit, which are temporarily exhausted, and when each one resets.

### Automation-First Requirement

AI subscription limits should not rely on manual entry unless no other option exists.

Preferred tracking methods, in order:

1. Official API or usage endpoint if available
2. Exported usage/billing data if available
3. Local browser/session-assisted script where safe and allowed
4. Screenshot/HTML capture parsed into structured data
5. Manual quick-correction field as fallback only

The dashboard should show data confidence:
- automatic
- imported
- inferred
- manual
- stale/unknown

### Subscription Fields

Each AI subscription/tool should support:

- Tool name
  - ChatGPT
  - Codex
  - Claude
  - Cowork
  - Other
- Subscription plan name
- Account/email label, if needed
- Account key hash, when available
- Account display name/email, when safely available
- Billing renewal date
- Monthly subscription cost
- Usage limit type
  - messages
  - prompts
  - credits
  - compute time
  - tokens
  - projects
  - other
- Limit amount, if known
- Limit window
  - daily
  - weekly
  - monthly
  - rolling window
  - unknown/manual
- Current used amount
- Remaining amount
- Percent used
- Percent used field name in JSON: `percent_used`
- Status
  - available
  - caution
  - near limit
  - exhausted
  - reset pending
  - unknown
- Reset date/time
- Reset countdown
- Notes about how the limit behaves
- Link to usage/settings/billing page
- Last checked date/time
- Tracking method
  - automatic
  - import
  - inferred
  - manual
  - unknown
- Data confidence
- Data freshness/staleness
- Whether value is sample/demo/real

### AI Limit Dashboard Widgets

The dashboard should include:

- AI capacity overview card
- “Best tool to use right now” recommendation
- Recommendation reasoning card
- “Available now” tools list
- “Near limit” warning list
- “Exhausted until reset” list
- Reset countdown cards
- Subscription cost summary
- Weekly usage trend
- Tool value vs. subscription cost
- Tool usefulness vs. limit pressure
- Script/check status per tool
- Manual “correct value” fallback only when needed
- Confidence/staleness badges per tool

### Provider-Neutral AI Session Count Requirement

Older specs included session count as a generic AI usage field. Keep this provider-neutral, not Codex-only.

Normalized AI usage snapshots should support:

- `session_count`

Rules:
- If one row represents one AI session, thread, or conversation, `session_count` defaults to `1`.
- If a collector/import emits aggregate rows, `session_count` stores the number of sessions, threads, or conversations represented by that row.
- Provider-native names such as thread count or conversation count may remain in collector metadata, but dashboard charts should normalize them to session count.
- Session count should be chartable by tool, project, account, model, day/week/month, and usable in value/recommendation logic alongside tokens, cost, capacity, and time spent.

Account-safe identity fields should be included where relevant:

- `account_key_hash`
- `account_label`
- `account_name`

### AI Usage Entry Fields

Each AI usage entry should support:

- Date
- Tool
- Subscription/account label
- Account key/hash, when available
- Account display name/email, when safely available
- Project
- Session title or short label
- Session count
  - default `1` for one session/thread/conversation row
  - aggregate count when one row summarizes multiple sessions
- Session type
  - planning
  - coding
  - troubleshooting
  - writing
  - image/design prompting
  - research
  - automation/scripting
  - other
- Time spent
- Usage amount consumed, if known
  - message count
  - credit count
  - token count
  - compute minutes
  - other
- Cost/credits/tokens, if known
- Usefulness score
- Output quality score
- Scoring scale is still an open decision and should be defined before implementation.
- Did it save time?
- Estimated time saved
- Did it create follow-up work?
- Follow-up tasks
- Link to repo, chat, file, or output
- Notes
- Tags
- Capture method
  - automatic
  - imported
  - inferred
  - manual fallback
- Confidence
- Freshness/source timestamp

### Useful AI Usage Charts

The dashboard should eventually show:

- AI usage by tool
- AI usage by project
- Time spent using AI per day/week
- Cost/credits/tokens by tool when available
- Subscription capacity remaining by tool
- Reset timeline
- Usefulness score by tool
- Usefulness score by project
- AI time spent vs. estimated time saved
- Sessions that created the most follow-up work
- Top tools by actual value, not just usage volume
- Subscription cost vs. usefulness
- Data freshness/automation health

### AI Usage Design Direction

Use compact cards and charts rather than overwhelming logs.

Suggested widgets:
- Today's AI usage summary
- Weekly AI usage trend
- Tool comparison cards
- Subscription limit status cards
- Reset countdowns
- Best/worst usefulness list
- Cost/credit burn tracker
- AI sessions needing follow-up
- “Worth it?” value indicator
- Script status / last checked cards

## Automation Health

The dashboard should include a small automation health section showing:

- Last successful run per script
- Last failed run per script
- Data freshness
- Source confidence
- Errors needing attention
- What data was updated
- What data is stale
- One-click rerun buttons where practical

## Project Registry

The dashboard should support all projects, not just a small fixed list.

However, the home dashboard should not show every project equally. It should surface the most relevant active work and keep the rest accessible through filters/search.

### Project Hierarchy

Use a nested project model:

```txt
Top-level project / umbrella
  → subproject / workstream
    → task / metric / note / activity
```

This allows Drakkar Designs to contain multiple workstreams without flooding the top-level dashboard.

Example:

```txt
Drakkar Designs
  → Woodworking Projects
  → CNC / Woodworking Production
  → Cedar Garden/Decor Products
  → Social Media / Marketing
  → Meta Insights
  → Product Images / Marketplace Graphics
```

Other top-level projects should remain separate, including Airbnb/Wheelhouse, Finance/Admin, Moola-Matic, Books Projects, WoW/Gaming, Home/Tech, and Personal/Misc.


### Project Statuses

Each project should have a status:

- Active
- Paused
- Someday
- Archived
- Blocked
- Needs review

### Project Fields

Each project should support:

- Project name
- Project category
- Parent project / umbrella project
- Status
- Priority
- Current focus score
- Last activity date
- Next action
- Blockers
- Related repo(s)
- Related files/links
- AI tools used
- Best AI tool recommendation
- Time/activity signals
- Metrics/source freshness
- Notes file path

### Home Dashboard Rules

The main dashboard should prioritize:

- Active projects
- Blocked projects needing attention
- Projects with deadlines
- Projects with recent activity
- Projects with high 80/20 impact
- Projects with stale metrics that need checks

Paused, someday, and archived projects should still be searchable and available, but should not clutter the home page.

### Project Navigation

The dashboard should include:

- Project search
- Icon-based project navigation
- Category filters
- Parent/umbrella project filters
- Status filters
- Favorites/pinned projects
- Recently active projects
- “Needs attention” list
- Reorderable project nav

## Project Pages

Each project page should include:

- Overview
- Current status
- Priority
- Next actions
- Notes and decisions
- Blockers
- Related files/repos/links
- Time spent
- AI usage/sessions
- Metrics
- Progress timeline
- Recent activity
- 80/20 recommendation for what matters most next
- Source/automation status for project metrics
- Confidence/staleness labels for metrics

## Chart and Metrics Direction

The dashboard will likely use fewer charts than typical finance dashboard examples, but should turn regular information into useful visuals when it helps.

Desired chart concepts:

- 80/20 priority split
- Time spent by project
- AI usage by tool
- AI usage by project
- Project-first AI recommendation cards
- AI subscription remaining capacity
- AI reset schedule
- AI usefulness by project/tool
- Weekly project activity
- Project health/status
- Automation freshness/status
- Data confidence distribution
- Trend lines from scheduled script outputs
- Fading gradient line/area charts

Avoid charts that look impressive but do not help decision-making.

## Visual Style

### Overall Direction

Premium futuristic dark-mode SaaS dashboard with violet/cobalt glow, glassy panels, and fading charts.

### Style Keywords

- Dark mode
- Purple
- Violet
- Cobalt
- Deep navy-purple background
- Soft glowing gradients
- Glassy rounded cards
- Gradient borders
- Fading line/area charts
- Elegant command-center feel
- Modern analytics UI
- High-end but usable

### Avoid

- Gamer neon overload
- Crypto exchange clone
- Generic AI template look
- Too many tiny charts
- Visual clutter
- Glow on every single element

### Reference Direction

Use these references as style inspiration, not pixel-for-pixel copies:

- Glow inspiration:
  - AI Powered Crypto Investment Landing Page UI
  - https://dribbble.com/shots/27087667-AI-Powered-Crypto-Investment-Landing-Page-UI

- Layout inspiration:
  - Futuristic SaaS Dashboard / Analytics Website Platform
  - https://dribbble.com/shots/27385741-Futuristic-SaaS-Dashboard-Analytics-Website-Platform

- Color/layout inspiration:
  - Dashboard for finance analytics
  - https://www.behance.net/gallery/116096995/Dashboard-for-finance-analytics

- Fading chart inspiration:
  - Dashboard Style Reports image
  - https://mygarbagecollection.com/wp-content/uploads/2026/04/Dashboard-Style-Reports.webp

## Build Approach

Recommended phased build:

1. Beautiful static dashboard with sample data
2. Real local data structure
3. Automation-first import/scanning architecture
4. AI usage acquisition collector design
5. Editable fallback fields for projects/tasks/time/AI usage
6. AI subscription limit/reset tracker
7. Data confidence/staleness badges
8. Source-specific freshness warning thresholds
9. Scheduled script imports
10. Automation health/status panel
11. Tailscale phone access
12. PWA polish
13. Phased customization expansion
14. Optional public hosting or login later if needed

## Suggested File Structure

```txt
dashboard/
  data/
    imports/
      ai_usage_daily.json
      ai_subscription_limits.json
      repo_activity.json
      meta_insights.json
      wheelhouse_metrics.json
  projects/
    drakkar-designs.md
    cnc-flags.md
    social-media.md
  app.db
  scripts/
    check_ai_limits/
    import_meta_insights/
    import_wheelhouse/
    scan_repos/
  src/
  docs/
    dashboard_master_spec_v4.38.md
```

## Example AI Subscription Limits JSON

```json
[
  {
    "tool": "ChatGPT",
    "plan": "Plus/Pro/etc",
    "account_label": "primary",
    "account_key_hash": null,
    "account_name": null,
    "limit_type": "messages",
    "limit_window": "rolling/daily/weekly/monthly/unknown",
    "limit_amount": null,
    "used_amount": null,
    "remaining_amount": null,
    "percent_used": null,
    "status": "unknown",
    "reset_at": null,
    "last_checked_at": "2026-06-26T00:00:00-04:00",
    "tracking_method": "automatic_or_import_preferred",
    "data_confidence": "unknown",
    "data_freshness": "never_checked",
    "is_sample_data": false,
    "notes": "Manual entry is fallback only. Exact behavior may vary by plan/model."
  }
]
```

## Codex Direction Draft

Build an extremely polished dark-mode personal command-center dashboard as a mobile-responsive Next.js web app with PWA support. Start local-first with SQLite, JSON imports, Markdown project files, and automation-first data collection. The dashboard should work well on desktop and phone and be accessible privately through Tailscale.

Use a premium futuristic SaaS aesthetic: near-black navy/purple background, cobalt blue and violet accent colors, soft radial glow effects, gradient borders, glassy dark cards, fading gradient line/area charts, clean typography, and strong spacing. The design should feel elegant, high-end, atmospheric, and useful — not like a crypto exchange clone, gamer UI, or generic template.

The home page should use Daily/Weekly/Monthly top timeframe tabs, icon-based left project navigation, and draggable, grid-resizable, persistent dashboard cards. V1 may keep some navigation fixed, but the long-term goal is customizable/reorderable navigation, project icons, card layouts, groups, and saved views wherever practical. It should show a compact command-center overview with a Daily view that includes Today’s Top 3. Today’s Top 3 should be auto-suggested from priority, urgency, blockers, recent activity, stale data, 80/20 impact, and AI availability, but manually overrideable/pinnable by Lauren: today’s priorities, active project cards, project registry/search access, 80/20 focus list, time spent by project, AI usage tracking, AI subscription limit/reset status, automation health, recent activity, blockers, quick capture, and links to detailed project pages.

The system should support all projects through a project registry with statuses like active, paused, someday, archived, blocked, and needs review. The home page should only surface the most relevant active/urgent projects. Each project page should show status, priority, next actions, blockers, notes, related files/repos/links, time spent, AI sessions, metrics, source confidence, automation freshness, and a progress timeline.

The AI Tools / Usage section should prioritize subscription-based usage tracking and include a clear acquisition process using official APIs/exports/pages/CLI output first, browser-assisted local capture second, and manual correction only as fallback. In v1, availability/limits should get the main dashboard space, while usefulness/value should still be tracked for subscription decisions. It must show which AI tools are available, which are near/exceeded limits, when limits reset, how much capacity remains, which tool is best to use right now using a project-first score of available capacity, project fit, project-specific usefulness, and optional task-type fit, why that tool is recommended, and whether each subscription is providing value. API token/cost tracking should be supported but secondary.

The system must be automation-first. Do not make manual entry the primary workflow. Use scripts, imports, repo scans, exports, parsed data, and inferred data whenever possible. Manual entry should only be used for quick corrections, missing values, emergency overrides, or temporary fallbacks.

Do not hide uncertain or stale data. Show last-known values when useful, but clearly label source, confidence, freshness, and last checked time. Important metrics should have confidence/staleness badges so the user can tell what is fresh, stale, inferred, manual, or unknown.

Use mock/sample data first, but structure the app so real data can later come from Markdown project notes, JSON script outputs, repo activity summaries, external metric scripts, and SQLite.

## Standing Safety Requirements

- Never print, log, export, or store raw access tokens, refresh tokens, cookies, authorization headers, or auth file contents.
- Store sanitized snapshots and aggregate metrics only.
- Keep token/auth safety rules visible during collector implementation.
- Store safe project labels by default.
- Raw workspace paths are local-only opt-in data and should not appear in dashboard display or exports.
- Account display labels such as email/name are local display fields. Use `account_key_hash` as the canonical grouping key.
- Do not expose prompt previews, first user messages, raw logs, raw rollout files, or full workspace paths by default.
- Scheduled collectors should only be enabled after user-triggered collectors are working safely.


## Implementation Readiness

Final Codex sanity check result:
- Good enough to begin implementation.
- No must-fix blockers found.
- Final safety tightening applied:
  - raw endpoint payloads must not be stored in the dashboard database or exports
  - temporary raw endpoint debugging must be manually enabled, local-only, short-lived, and must never include raw tokens, cookies, authorization headers, or auth file contents

## First Implementation Slice

Now that the master spec is cleaned and implementation-ready, stop expanding the spec and build the first thin slice.

Chosen first slice:

```txt
Codex Usage Card
```

Pipeline:

```txt
local Codex live-usage collector
→ sanitized JSON snapshot
→ SQLite row
→ FastAPI endpoint
→ first dashboard card
```

Recommended stack:

```txt
Backend: Python FastAPI
Database: SQLite
Collectors: Python scripts
Frontend: React + Vite
UI: Tailwind first, draggable card grid later
Access: local network / Tailscale
```

Initial repo structure:

```txt
dashboard/
  backend/
    app/
    collectors/
    db/
  frontend/
  data/
    raw/
    sanitized/
  docs/
    dashboard_master_spec_v4.38.md
```

First collector:

```txt
collect_codex_live_usage.py
```

Collector requirements:
- read existing Codex auth safely
- never print/store raw tokens, cookies, auth headers, or auth file contents
- call sanitized `/wham/usage` collector path
- extract sanitized fields only
- derive `account_key_hash`
- include local-only account label if available
- write sanitized JSON snapshot
- insert/update SQLite row

First API endpoint:

```txt
GET /api/ai/codex/live-usage
```

First dashboard card should show:
- account label
- plan type
- 5-hour usage percent
- weekly usage percent
- reset credits
- reset countdowns
- freshness badge

Implementation principle:
- Build this complete narrow pipeline before adding more dashboard cards.


## Startup / Autostart Plan

Requirement:
The dashboard should be able to start on its own when the computer starts or when the user logs into Windows.

Preferred v1 approach:
Use Windows Task Scheduler instead of a Windows Service.

Reason:
- Easier to create, edit, disable, and troubleshoot.
- Works well for a personal local dashboard.
- Can run at user logon.
- Can start the backend server and/or collector runner.
- Does not require packaging the app as a formal Windows service at first.

Phase 1 startup behavior:
- Start the FastAPI backend at Windows logon.
- Optionally start the frontend dev/build server if still in development.
- Do not auto-run scheduled collectors until the user-triggered collector is confirmed safe.
- Once collector safety is confirmed, add a scheduled collector task separately.

Recommended startup tasks:
1. `Dashboard Backend`
   - Trigger: at user logon
   - Action: run backend start script
   - Purpose: start local FastAPI API server

2. `Dashboard Collector Runner`
   - Trigger: delayed after logon or every X minutes
   - Action: run safe collector script
   - Purpose: update sanitized snapshots
   - Enable only after manual collector is proven safe

3. `Dashboard Frontend`
   - Development only: run Vite dev server at logon
   - Production later: serve built frontend through backend or a small local static server

Preferred future production model:
- Build frontend into static files.
- FastAPI serves the API and optionally the built frontend.
- One startup task starts the backend/dashboard app.
- Separate scheduled task runs collectors.

Safety:
- Startup scripts must not print tokens.
- Startup logs must be sanitized.
- Collector tasks should write only sanitized JSON/SQLite rows.
- Raw debug capture must remain disabled by default.

Non-goal for v1:
- Do not create a Windows Service until Task Scheduler is insufficient.
- Do not enable background collection before user-triggered collection is safe.


## Self-Learning / Memory / Token-Efficiency Skill Strategy

Purpose:
Improve Codex continuity and reduce wasted tokens without adding unsafe autonomous behavior or overcomplicating Phase 1.

### Recommendation

Use lightweight repo-local learning and token-efficiency rules first.

Do not add heavy self-evolving agent frameworks, screen-memory systems, background recall systems, or aggressive token-proxy tools during Phase 1.

### Safe Self-Learning For This Repo

Use “self-learning” as structured repo memory, not autonomous hidden learning.

Allowed Phase 1 memory artifacts:
- `AGENTS.md`
- `docs/handoff.md`
- `docs/decisions.md`
- `docs/runbook.md`
- `docs/phase_1_status.md`
- short per-session handoff summaries
- implementation notes that are reviewed before becoming permanent instructions

Rules:
- Codex may propose updates to repo memory files.
- Codex must not silently change project rules.
- Durable lessons should be reviewed and committed as Markdown.
- Do not store secrets, raw auth paths, prompt previews, raw logs, or raw endpoint payloads in memory files.
- Keep memory high-signal and short.
- Prefer “what to do next / what was decided / what to avoid” over chat transcripts.

Recommended self-learning skill categories:
1. Handoff / session-summary skill
   - Compresses the session into clean continuation notes.
   - Best immediate value for this long-running dashboard repo.

2. Decision-log skill
   - Turns confirmed decisions into durable `docs/decisions.md` entries.
   - Prevents progress logs from polluting the master spec.

3. Repo-instructions / AGENTS.md skill
   - Maintains concise standing instructions for Codex.
   - Should point to the current master spec and Phase 1 scope.

4. Runbook-maintainer skill
   - Updates setup/run/test instructions as implementation changes.
   - Useful for preventing “works once but cannot restart” problems.

Avoid during Phase 1:
- autonomous self-modifying memory
- hidden background learning
- screen/screenshot memory systems
- long raw conversation memory dumps
- any memory that stores tokens, endpoint payloads, logs, prompts, or full paths

### Token-Efficiency Strategy

Use simple token hygiene before adding external tools.

Phase 1 token-efficiency rules:
- Codex should read the master spec summary sections first, not every old version.
- Codex should inspect only files it needs for the current task.
- Codex should summarize large files before editing.
- Codex should avoid pasting full logs, full DB dumps, or full endpoint payloads.
- Codex should prefer targeted grep/search over reading whole directories.
- Codex should keep handoff notes short and structured.
- Codex should ask before using multi-agent loops or broad repo scans.
- Codex should not run repeated exploratory commands after a source is confirmed.
- Codex should use small commits/checkpoints where possible.

Recommended token-efficiency skill categories:
1. Context compression / context optimization skill
   - Use for long sessions and handoffs.
   - Goal: preserve decisions and next actions, not compress everything blindly.

2. Code search / repo map skill
   - Use targeted symbol/file search to avoid loading unnecessary files.
   - Helpful after the repo grows.

3. CLI-output compression skill
   - Use for command output, logs, and test failures.
   - Must preserve actionable error lines.
   - Must not hide security-relevant warnings.

4. Cost/router/preflight skill
   - Use to decide when a task needs high reasoning vs. simple edit mode.
   - Should not override Phase 1 scope or safety rules.

5. Security-aware summarizer
   - Summarizes logs/output while redacting secrets and avoiding raw payload storage.

### Relevant Current References / Repos

Use as references or catalogs, not automatic installs:

- OpenAI skills docs and official skill catalog:
  - `https://developers.openai.com/codex/skills`
  - `https://github.com/openai/skills`

- AGENTS.md:
  - `https://agents.md/`
  - Use for repo-level standing instructions.

- `muratcankoylan/agent-skills-for-context-engineering`
  - Useful reference for context engineering, context compression, and context optimization skills.

- GitHub token optimization / token savings topics
  - Useful for discovering tools such as code-search/context tools.
  - Examples seen in search:
    - `jgravelle/jcodemunch-mcp`
    - `Houseofmvps/codesight`
    - `TokenTamer`
    - `tokless`

- `HelloWorld668/codex-token-optimizer`
  - Codex Agent Skill for token optimization using output compression tools.
  - Treat as experimental until reviewed.

- `zx1160763849-hash/codex-cost-router-skills`
  - Preflight routing idea for reducing token waste.
  - Treat as experimental until reviewed.

- `JuliusBrussee/caveman`
  - Token-minimal communication style / agent approach.
  - Interesting reference, but likely too aggressive for this repo unless explicitly chosen.

### Phase 1 Decision

For Phase 1, default to these only:
- handoff/session-summary
- AGENTS.md/repo-instructions
- decision-log/runbook maintenance
- context-compression for long sessions
- targeted search / repo-map behavior
- security-aware output summarization

Do not install token-proxy, MCP, self-evolving, or autonomous memory tools until:
- Phase 1 works,
- safety is verified,
- and Lauren explicitly approves the tool.

### Codex Prompt Add-On

When sending Phase 1 to Codex, add:

```txt
Also check for lightweight self-learning and token-efficiency skills.

Use only safe, repo-local learning:
- AGENTS.md
- handoff summaries
- decision log
- runbook updates
- short reviewed project memory

Do not add hidden autonomous memory, screenshot/screen memory, background recall, self-modifying agents, or raw transcript memory.

For token efficiency, prefer:
- targeted file search
- repo map/code search
- context compression for handoffs
- concise command-output summaries
- security-aware log summarization

Do not install experimental token proxies, MCP tools, or self-evolving frameworks unless I explicitly approve them.
Report any recommended self-learning or token-efficiency skills separately before installing them.
```


## Build-It-Right-First-Time Repo Strategy

Purpose:
Add the highest-leverage tooling, references, and guardrails before Phase 1 implementation so the repo starts clean and stays maintainable.

This section comes from current web research across official docs, current skill catalogs, recent package/tool releases, and dashboard/full-stack references.

### Core Principle

Use a boring, safe, narrow stack for Phase 1.

Add tools that prevent mistakes:
- secrets scanners
- simple task runner
- formatting/linting
- type-safe API boundary
- small tests
- clear repo instructions
- runbook/decision log

Avoid tools that add scope:
- SaaS templates
- cloud deployment
- login/auth frameworks
- RAG/vector databases
- external automation actions
- heavy observability
- multi-agent frameworks
- MCP/tool servers unless explicitly approved later

### Recommended Repo Quality Pack

Add these early:

1. `AGENTS.md`
   - Repo-level instructions for Codex and other coding agents.
   - Include setup commands, test commands, Phase 1 scope lock, safety rules, and where to find the master spec.

2. `docs/decisions.md`
   - Short Architecture Decision Record style log.
   - Record durable decisions only.
   - Do not use it as a transcript dump.

3. `docs/runbook.md`
   - How to start/stop backend.
   - How to run collector manually.
   - How to initialize database.
   - How to verify output is sanitized.

4. `docs/handoff.md`
   - Short current status and next action.
   - Used to reduce Codex context/tokens between sessions.

5. `.env.example`
   - Safe configuration names only.
   - No real secrets or tokens.
   - Do not reference raw local auth paths beyond generic Codex home setting.

6. `.gitignore`
   - Must ignore:
     - local DB files if desired
     - raw/debug folders
     - auth files
     - logs
     - `.env`
     - node/python caches
     - generated raw payload captures
   - Sanitized snapshots may be allowed only if explicitly safe.

7. `Taskfile.yml` or `justfile`
   - One predictable place for commands.
   - Recommended commands:
     - setup backend
     - setup frontend
     - init db
     - run collector
     - run backend
     - run frontend
     - test
     - lint
     - scan secrets

Recommendation:
- Prefer `Taskfile.yml` for Windows-friendliness and self-documenting task descriptions.
- `justfile` is also good, but Taskfile has stronger cross-platform positioning.

### Python Backend / Collector Tooling

Recommended:

1. `uv`
   - Use for Python dependency/project management.
   - Fast and modern.
   - Good default for a new Python repo.

2. `ruff`
   - Use for Python linting and formatting.
   - Replaces multiple older tools for this repo’s needs.
   - Keep config simple.

3. `pytest`
   - Use for small backend/collector tests.
   - Required Phase 1 tests:
     - auth parser never returns token in serialized metadata
     - mapper outputs sanitized fields only
     - DB insert works
     - API response contains no forbidden fields

4. `pydantic-settings`
   - Use for backend configuration.
   - Supports typed settings and environment-based config.
   - Do not store secrets in `.env`; use it for paths/ports/options only.

5. `Typer`
   - Use if collector CLI needs subcommands.
   - Useful commands:
     - collect-codex-live
     - init-db
     - show-latest
     - health

6. `Rich`
   - Optional for safe manual collector output.
   - If used, show only sanitized values.
   - Never print token-like strings.

7. Structured logging
   - Start with standard Python logging if simplest.
   - Consider `structlog` later if collector logs become hard to inspect.
   - Logs must be sanitized.

Database:
- Phase 1 should remain SQLite.
- Use `schema.sql` + simple DB helper first.
- Consider SQLModel only if CRUD/model complexity grows.
- Do not adopt PostgreSQL/Alembic/Docker in Phase 1 unless the project outgrows simple SQLite.

### Frontend Tooling

Recommended:

1. React + Vite + TypeScript
   - Keep frontend fast and simple.
   - Use TypeScript from the start.

2. Tailwind + shadcn/ui
   - Good fit for card UI.
   - Use only the components needed for Phase 1.
   - Do not import a full template before the first card works.

3. TanStack Query
   - Use for API data fetching, caching, stale/fresh behavior, retries, and refetch control.
   - Good match for freshness badges and collector-driven data.

4. TanStack Router
   - Defer until there is more than one real page.
   - Phase 1 can use a single page with simple component structure.

5. Recharts
   - Good chart library for React cards.
   - Optional in Phase 1 unless usage bars/countdowns are enough.
   - More useful in Phase 2 for historical usage trends.

6. Lucide React
   - Use for consistent icon set.
   - Import only icons needed.

7. Vitest
   - Use for frontend unit/component tests once frontend card exists.

8. Playwright
   - Optional Phase 1 smoke test:
     - backend running
     - frontend loads
     - Codex card displays sanitized fields
   - Do not overbuild E2E suite in Phase 1.

9. MSW
   - Useful if frontend card needs to be developed before real API is stable.
   - Use for mocked sanitized API responses only.
   - Do not mock raw endpoint payloads containing sensitive fields.

### API Type-Safety / Client Generation

High-value addition:
- Use FastAPI’s generated OpenAPI schema as the frontend contract.
- Generate TypeScript client/types after the first API endpoint stabilizes.

Recommended tools to consider:
- Hey API / `@hey-api/openapi-ts`
- Orval
- openapi-typescript + openapi-fetch / openapi-react-query

Phase 1 recommendation:
- Do not block the first vertical slice on codegen.
- Once `GET /api/ai/codex/live-usage` stabilizes, generate the client/types so the frontend card does not drift from the backend response schema.

### JavaScript Package / Formatting Tooling

Recommended:

1. `pnpm`
   - Good default for frontend package management.
   - Recent pnpm versions emphasize stronger security defaults.
   - Use lockfile.

2. Biome or ESLint/Prettier
   - For Phase 1, choose one.
   - Biome is attractive because it combines fast formatting and linting for TypeScript/JS/CSS/JSON.
   - If shadcn/tooling expects ESLint/Prettier patterns, do not fight it; keep defaults simple.

Recommendation:
- Use pnpm.
- Use Biome if Codex confirms no conflict with Vite/shadcn setup.
- Otherwise use the default Vite/TypeScript linting path and avoid bikeshedding.

### Secret / Safety Tooling

This repo should treat secret scanning as Phase 1 infrastructure, not later polish.

Recommended:

1. Gitleaks
   - Fast secret scanner for repos/files/stdin.
   - Good local pre-commit/default scan candidate.

2. TruffleHog
   - Better as optional/deeper verification scan.
   - Useful for history/deeper checks.
   - May be slower/noisier than Gitleaks for every commit.

3. GitHub Secret Scanning / Push Protection
   - Enable if repo is on GitHub and available.
   - Blocks or alerts on pushed secrets.

4. detect-secrets
   - Optional if a baseline workflow is desired.
   - More useful for legacy repos; probably not needed immediately for a clean new repo.

Phase 1 recommendation:
- Use Gitleaks locally/pre-commit if easy.
- Use TruffleHog as manual/deeper scan before major pushes.
- Enable GitHub push protection if repo is hosted on GitHub.
- Do not rely on one scanner only if auth/token work continues.

### Testing / Verification Strategy

Minimum Phase 1 checks:

Backend/collector:
- unit test token discovery helper with fake token-shaped data
- test token is never serialized
- test JWT claim decode with fake JWT
- test mapper with fake `/wham/usage` payload
- test DB insert and latest query
- test API returns only sanitized fields

Frontend:
- render Codex Usage card with mocked sanitized API data
- verify account label/plan/quota values display
- verify forbidden fields are absent

Secret scan:
- scan repo before first commit
- scan before sending repo to Codex if files include local data
- scan before any GitHub push

Manual verification:
- run collector manually
- inspect sanitized JSON
- inspect SQLite latest row
- call API endpoint
- view frontend card
- confirm no secrets appear in console/logs/DB/API/UI

### Current References / Sources To Use

Official/current sources:
- OpenAI Codex skills docs and `openai/skills`
- AGENTS.md format
- FastAPI docs and FastAPI full-stack template
- SQLModel docs as optional future ORM reference
- shadcn/ui Vite docs
- TanStack Query docs
- TanStack Router docs for later multi-page navigation
- uv docs
- Ruff docs
- pytest docs
- Pydantic Settings docs
- Typer docs
- Rich docs
- Taskfile docs
- pnpm docs and pnpm 11 release notes
- Biome docs
- Gitleaks docs
- TruffleHog pre-commit docs
- GitHub Secret Scanning / Push Protection docs
- Hey API / Orval / OpenAPI TypeScript docs
- Vitest docs
- Playwright docs
- Recharts docs
- Lucide docs
- MSW docs

Reference only, do not adopt wholesale:
- FastAPI full-stack template
- `satnaing/shadcn-admin`
- awesome agent/codex skill catalogs
- context-engineering/token-efficiency skill repos

### Phase 1 Additions Worth Making

Before Codex starts coding, add these to the Phase 1 scope if feasible:

- `AGENTS.md`
- `Taskfile.yml` or `justfile`
- `.env.example`
- `.gitignore`
- `docs/runbook.md`
- `docs/decisions.md`
- `docs/handoff.md`
- basic Ruff config
- basic pytest structure
- basic secret scan command
- safe fake fixtures for tests
- frontend package manager decision: pnpm
- frontend API mock strategy: MSW only if needed
- later API type generation: Hey API / Orval after endpoint stabilizes

### Phase 1 Avoid List Expanded

Avoid:
- adopting a large template wholesale
- SQLModel/Alembic/Postgres/Docker unless needed
- authentication systems
- deployment/cloud hosting
- RAG/vector DB
- MCP server
- token proxy tools
- autonomous memory frameworks
- action-capable integration skills
- full E2E suite before one card works
- frontend routing complexity before multiple pages exist
- scheduler before manual collector proves safe

### Best Default Stack After Research

```txt
Python: uv + FastAPI + sqlite3/schema.sql + pydantic-settings + pytest + ruff
Collector CLI: plain Python first, Typer if subcommands are needed
Terminal output: plain print first, Rich optional for sanitized tables
Frontend: React + Vite + TypeScript + Tailwind + shadcn/ui
Frontend data: TanStack Query
Frontend charts/icons: Recharts later, Lucide now
Frontend tests: Vitest; Playwright smoke test later
Package manager: pnpm
Task runner: Taskfile preferred, just acceptable
Security: Gitleaks early, TruffleHog manual/deeper, GitHub push protection if hosted
Agent hygiene: AGENTS.md + handoff + decisions + runbook
API type-safety: Hey API / Orval after first API endpoint stabilizes
```

### Codex Add-On Prompt

Use this with Phase 1 handoff:

```txt
Before coding, also propose a minimal repo-quality setup for Phase 1.

Include:
- AGENTS.md
- Taskfile.yml or justfile
- .env.example
- .gitignore
- docs/runbook.md
- docs/decisions.md
- docs/handoff.md
- Python tooling: uv, ruff, pytest, pydantic-settings
- frontend tooling: React/Vite/TypeScript, pnpm, Tailwind/shadcn, TanStack Query
- security tooling: Gitleaks command or hook, optional TruffleHog manual scan
- test fixtures that use fake tokens/payloads only
- API type-generation plan after endpoint stabilizes

Do not add:
- cloud deployment
- external auth
- Postgres/Docker
- SaaS templates
- RAG/vector DB
- MCP server
- scheduled collectors
- autonomous memory
- any tool that stores raw endpoint payloads or secrets

Report any added tool before installing if it changes scope, adds background services, calls external systems, or could expose secrets.
```


## Phase 1 Skill / Reference Strategy

Purpose:
Use existing skills, catalogs, and reference repos to make the dashboard repo better without overbuilding Phase 1 or adopting a heavy template.

Rule:
Do not bulk-install a large skill pack. Use targeted skills only when they directly help Phase 1.

### Recommended Skills To Look For / Use

Use available Codex skills first, especially built-in or official skills when present.

Priority skill categories:

1. Planning / implementation-plan skill
   - Use to break Phase 1 into small safe commits.
   - Use before coding if the next step is ambiguous.

2. Handoff / session-summary skill
   - Use to create clean continuation notes between Codex sessions.
   - Especially useful because this project has a long spec and safety-sensitive collector work.

3. CLI creator / Python script skill
   - Use for durable collector scripts.
   - Relevant scripts:
     - `collect_codex_live_usage.py`
     - database init scripts
     - manual collector run commands
     - startup helper scripts

4. FastAPI API structure skill
   - Use only if it keeps the backend simple.
   - Helpful for route structure, app startup, dependency setup, and API response patterns.

5. SQLite / migrations / schema skill
   - Use for schema creation, migrations, and safe local DB setup.
   - Keep Phase 1 simple: SQLite first, no Postgres.

6. React + Vite + Tailwind / shadcn card UI skill
   - Use for the first Codex Usage card and basic dashboard styling.
   - Do not let this expand into a full admin template before Phase 1 works.

7. Security / secrets review skill
   - Use after collector work and before committing.
   - Must verify no tokens, cookies, auth headers, auth file contents, raw endpoint payloads, prompt previews, raw logs, or full workspace paths are stored, printed, committed, or returned by the API.

8. Test / review skill
   - Use for small checks:
     - collector produces sanitized output
     - DB insert works
     - API response matches schema
     - frontend card renders safe fields
     - no secret-like values appear in snapshots/logs/API

9. Repo instructions / AGENTS.md skill
   - Use to create or refine repo-specific instructions for Codex.
   - Must point Codex at the current master spec and Phase 1 scope lock.

### Skill Catalogs To Use As Search Sources

Use these as catalogs/shopping lists, not as bulk installs:

1. OpenAI Codex Skills docs / official skills catalog
   - Use official or built-in skills first when available.
   - Source:
     - `https://developers.openai.com/codex/skills`
     - `https://github.com/openai/skills`

2. VoltAgent `awesome-agent-skills`
   - Large curated collection of agent skills compatible with Codex and other coding agents.
   - Use as a discovery catalog only.
   - Source:
     - `https://github.com/VoltAgent/awesome-agent-skills`

3. ComposioHQ `awesome-codex-skills`
   - Codex-focused skill catalog.
   - Use carefully because some skills perform external actions.
   - Do not add email/Slack/GitHub-action skills unless explicitly approved.
   - Source:
     - `https://github.com/ComposioHQ/awesome-codex-skills`

4. Other community skill catalogs
   - Search only if the official/catalog skills do not cover a need.
   - Avoid overlapping skills that give conflicting instructions.

### Reference Repos / Templates

Use references for ideas. Do not clone a large template over the repo unless explicitly approved.

1. `satnaing/shadcn-admin`
   - Use as UI/card/layout inspiration.
   - Good for shadcn + Vite dashboard patterns.
   - Note: it describes itself as not a starter project/template, so use it as a reference.
   - Source:
     - `https://github.com/satnaing/shadcn-admin`

2. FastAPI full-stack template
   - Use as backend organization reference only.
   - It is too heavy for Phase 1 because it includes PostgreSQL, Docker, deployment, auth, and production scaffolding.
   - Source:
     - `https://github.com/fastapi/full-stack-fastapi-template`

3. Lightweight shadcn/admin dashboard roundups
   - Use for visual ideas only.
   - Do not adopt a full SaaS/admin kit before Phase 1 works.

### Avoid For Phase 1

Avoid adding:
- full SaaS templates
- cloud deployment templates
- external auth systems such as Auth0
- billing/subscription frameworks
- RAG/vector database frameworks
- external monitoring/observability stacks
- email/Slack/GitHub automation skills that take outside actions
- Docker/Postgres/Traefik/Caddy unless Phase 1 truly needs them
- heavy Next.js/monorepo templates
- multiple overlapping frontend design skills
- automatic scheduled collectors before manual collector safety is proven
- any skill that encourages storing raw payloads, auth headers, or secrets

### Phase 1 Skill Use Rules

Codex should:
- search available local/official skills before building from scratch
- choose the smallest number of skills that directly help Phase 1
- explain which skills it plans to use and why
- explain which tempting skills/templates it is skipping and why
- avoid skills that change the Phase 1 scope
- stop and ask before installing/adopting any large template or action-capable skill

### Skill Discovery Prompt For Codex

Use this before Phase 1 coding:

```txt
Before implementing Phase 1, search the local/available skill catalogs for existing skills that can help with this repo.

Prioritize skills for:
- FastAPI API structure
- SQLite schema/migrations
- Python CLI collector scripts
- secret-safety/security review
- React + Vite + Tailwind/shadcn dashboard cards
- test/review workflow
- handoff/session summary
- repo instructions / AGENTS.md

Do not bulk-install a large skill pack.

Use existing skills only if they directly help Phase 1. Avoid overlapping skills that would give conflicting instructions. Do not add auth, cloud deployment, billing, external monitoring, RAG, or SaaS-template complexity.

Use external repos as references only unless explicitly approved:
- shadcn-admin style/layout ideas are allowed as references
- FastAPI full-stack template is allowed as a reference
- do not clone a large template over the repo
- do not expand beyond Phase 1

After checking available skills, report:
1. which skills you found
2. which ones you recommend using
3. which ones you recommend skipping
4. why
5. whether any skill changes the Phase 1 plan
```

### Recommendation

For Phase 1, the default should be:

Use:
- planning/review
- CLI/script creation
- FastAPI basics
- SQLite basics
- React/Vite/Tailwind card UI
- security/secrets review
- handoff/session summary

Reference only:
- `satnaing/shadcn-admin`
- FastAPI full-stack template
- curated skills catalogs

Avoid:
- large templates
- cloud/auth/billing/RAG/monitoring stacks
- external action skills
- anything that expands Phase 1 beyond the Codex Usage Card pipeline


## Codex Phase 1 Handoff Instructions

Use this section when handing the spec to Codex for Phase 1 implementation.

### Phase 1 Scope Lock

Implement Phase 1 only.

Build:
- repo skeleton
- backend foundation
- SQLite schema/init
- safe Codex auth reader
- safe Codex live usage collector
- sanitized JSON snapshot writer
- SQLite insert/update
- collector run logging
- FastAPI endpoint
- one Codex Usage frontend card
- basic startup/run scripts
- quick start documentation

Do not build:
- Phase 2 Daily dashboard cards
- project registry UI
- draggable/resizable grid
- Claude/ChatGPT collectors
- scheduled background collectors
- recommendation engine
- notifications
- calendar/email integrations
- full mobile/PWA polish

### Implementation Style

Codex should:
- build the smallest complete working pipeline first
- prefer boring/simple code over clever architecture
- keep files readable and locally maintainable
- avoid adding extra frameworks unless clearly needed
- create clear run commands
- include basic tests or manual verification steps
- update docs when setup/run behavior changes
- stop and ask before changing scope

### Security Rules for Implementation

Never print, log, export, store, commit, or expose:
- access tokens
- refresh tokens
- cookies
- authorization headers
- auth file contents
- raw endpoint payloads in dashboard DB or exports
- prompt previews
- first user messages
- raw logs
- raw rollout files
- full workspace paths by default

Allowed:
- sanitized snapshots
- hashed account keys
- local-only account labels
- safe project labels
- aggregate usage metrics
- freshness/confidence metadata
- temporary local debug capture only if manually enabled, short-lived, and never containing auth secrets

### Required Phase 1 Deliverables

Codex should produce:
1. File/folder changes summary.
2. How to install dependencies.
3. How to initialize the database.
4. How to run the collector manually.
5. How to start the FastAPI backend.
6. How to start the frontend.
7. How to verify the API returns sanitized data.
8. How to verify the frontend card displays it.
9. Where sanitized JSON snapshots are written.
10. Confirmation that no raw secrets are stored or printed.

### First Task for Codex

Start by creating the Phase 1 repo skeleton and backend collector foundation.

First files to prioritize:
- `backend/collectors/codex_auth.py`
- `backend/collectors/collect_codex_live_usage.py`
- `backend/collectors/codex_usage_mapper.py`
- `backend/db/schema.sql`
- `backend/app/db.py`
- `backend/app/main.py`
- `backend/app/routes/ai_codex.py`

After that:
- create the frontend Codex Usage card
- add run scripts/docs
- add startup notes



## Phase 1 Implementation Plan

Goal:
Build the smallest complete working dashboard pipeline before adding more tools/cards.

Phase 1 target:

```txt
Codex Usage Card v1
```

Assumed v1 stack unless changed:
- Python collectors
- SQLite local database
- FastAPI backend
- React + Vite frontend
- Tailwind for UI styling
- Local/Tailscale access first

### Phase 1 Build Order

#### 1. Repo Skeleton

Create the project structure:

```txt
dashboard/
  backend/
    app/
      main.py
      db.py
      models.py
      routes/
        ai_codex.py
    collectors/
      collect_codex_live_usage.py
      codex_auth.py
      codex_usage_mapper.py
    db/
      schema.sql
  frontend/
  data/
    sanitized/
      codex/
  docs/
    dashboard_master_spec_v4.38.md
```

Rules:
- No raw secrets in repo.
- No raw auth files copied into repo.
- `data/sanitized/` may contain safe JSON snapshots only.
- Any debug/raw folder must be gitignored and disabled by default.

#### 2. SQLite Schema v1

Create tables for:

```txt
ai_accounts
ai_usage_snapshots
collector_runs
```

Minimum fields:

`ai_accounts`
- `account_key_hash`
- `provider`
- `account_label`
- `account_name`
- `auth_mode`
- `created_at`
- `updated_at`

`ai_usage_snapshots`
- `id`
- `provider`
- `tool`
- `account_key_hash`
- `plan_type`
- `reset_credits_available`
- `quota_5h_used_percent`
- `quota_5h_remaining_percent`
- `quota_5h_reset_at`
- `quota_weekly_used_percent`
- `quota_weekly_remaining_percent`
- `quota_weekly_reset_at`
- `session_count`
- `source_type`
- `source_label`
- `confidence`
- `freshness`
- `collected_at`

`collector_runs`
- `id`
- `collector_name`
- `started_at`
- `finished_at`
- `status`
- `safe_message`
- `records_written`

#### 3. Codex Auth Reader

Create `codex_auth.py`.

Responsibilities:
- locate Codex auth in the existing Codex home
- read token only in memory
- decode safe identity claims
- compute `account_key_hash`
- return sanitized account metadata
- never print or write raw token values

Returned object should include:
- `access_token` in memory only
- `account_key_hash`
- `account_label`
- `account_name`
- `auth_mode`
- `last_refresh`

Safety:
- `access_token` must not be included in normal logs, JSON snapshots, DB rows, API responses, or frontend props.

#### 4. Codex Live Usage Collector

Create `collect_codex_live_usage.py`.

Responsibilities:
- call the Codex live quota endpoint
- map response into sanitized fields
- write one sanitized JSON snapshot
- insert/update SQLite rows
- record collector run status

Output should include:
- account label
- plan type
- 5-hour usage percent
- weekly usage percent
- reset credits
- reset timestamps
- collected timestamp
- confidence/freshness

Output must not include:
- access token
- refresh token
- raw authorization header
- full auth file
- raw endpoint payload by default

#### 5. FastAPI Endpoint

Create endpoint:

```txt
GET /api/ai/codex/live-usage
```

Return latest sanitized snapshot grouped by account.

Response shape:

```json
{
  "accounts": [
    {
      "account_key_hash": "...",
      "account_label": "...",
      "account_name": "...",
      "plan_type": "...",
      "reset_credits_available": 0,
      "quota_5h": {
        "used_percent": 0,
        "remaining_percent": 100,
        "reset_at": "timestamp"
      },
      "quota_weekly": {
        "used_percent": 0,
        "remaining_percent": 100,
        "reset_at": "timestamp"
      },
      "freshness": "fresh",
      "confidence": "high",
      "collected_at": "timestamp"
    }
  ]
}
```

#### 6. Frontend Card v1

Create a single card first:

```txt
Codex Usage
```

Card shows:
- account label
- plan type
- 5-hour used/remaining percent
- weekly used/remaining percent
- reset credits
- reset countdowns
- freshness/confidence badge
- last collected time

No draggable grid yet.
No full dashboard navigation yet.
No extra AI tools yet.

#### 7. Definition of Done

Phase 1 is done when:
- collector runs manually without printing secrets
- sanitized JSON snapshot is written
- SQLite row is inserted
- FastAPI endpoint returns latest snapshot
- React card displays the latest data
- stale/fresh badge works
- multiple accounts can be represented by `account_key_hash`
- raw tokens/auth data never appear in DB, JSON snapshots, API response, frontend, or console logs

### Phase 1 Non-Goals

Do not build yet:
- full Daily/Weekly/Monthly dashboard
- draggable/resizable card grid
- Claude collectors
- ChatGPT browser/session collector
- project recommendation engine
- full project registry UI
- mobile polish
- scheduled collectors
- notification system

### First Implementation Decision

Start with the backend/collector side before the frontend.

Immediate next file to build:

```txt
backend/collectors/collect_codex_live_usage.py
```



## Phase 1 Completion Checklist

Phase 1 is slightly more than the Codex card itself. It should include the small support pieces needed to run safely and restart reliably.

Phase 1 must include:

1. Repo skeleton
   - backend folder
   - frontend folder
   - docs folder
   - data folder
   - sanitized data folder
   - gitignore rules for secrets/raw debug files

2. Backend foundation
   - FastAPI app
   - health endpoint
   - SQLite connection helper
   - schema initialization

3. Codex collector
   - safe auth reader
   - account identity extraction
   - account key hashing
   - `/wham/usage` live quota call
   - sanitized mapper
   - sanitized JSON snapshot writer
   - SQLite insert/update
   - collector run logging

4. API endpoint
   - latest Codex usage by account
   - sanitized response only
   - freshness/confidence values

5. Frontend v1
   - one Codex Usage card
   - no full dashboard grid required yet
   - show account label, plan, 5-hour usage, weekly usage, reset credits, reset countdowns, freshness

6. Startup/run support
   - backend start script
   - optional frontend dev start script
   - Windows Task Scheduler plan/script
   - no auto-scheduled collector until manual collector is proven safe

7. Documentation
   - quick start instructions
   - safety rules
   - how to run collector manually
   - how to start/stop backend
   - known non-goals

Phase 1 is complete when:
- dashboard backend can start manually
- collector can run manually without exposing secrets
- SQLite stores sanitized data
- API returns latest sanitized Codex usage
- frontend card displays it
- dashboard can be configured to start at Windows logon
- no raw tokens/auth data appear in DB, JSON, logs, API, or frontend

Phase 1 is not required to include:
- Claude/ChatGPT collectors
- scheduled background collector
- full Daily/Weekly/Monthly views
- draggable card grid
- mobile polish
- project recommendation engine
- full project registry UI
- notifications


## Phase 1 → Phase 2 Gate Questions

When Phase 1 is complete, ask these questions before starting Phase 2. These are not meant to reopen the whole spec; they are a short gate check to decide how Phase 2 should be built.

### 1. Phase 1 Reality Check

- Did the Codex live collector run safely without printing or storing secrets?
- Did sanitized JSON and SQLite rows look correct?
- Did the API response match the frontend card needs?
- Did startup/run support work reliably?
- Was anything annoying, fragile, slow, or confusing during Phase 1?

### 2. Data Safety Check

- Did any raw token, auth header, auth file content, prompt text, raw project path, or raw endpoint payload accidentally appear in logs, JSON, DB, API, frontend, or exports?
- Should any extra safety guard be added before adding more cards or collectors?

### 3. Project Registry Decision

Choose the Phase 2 project registry starting model:

```txt
A. SQLite table only
B. Markdown/JSON project files + SQLite index
```

Recommended default:
- Start with SQLite table only.
- Add Markdown export/import later if needed.

### 4. Daily Dashboard Card Priority

Pick the Phase 2 card order:

Recommended default:
1. Codex Usage
2. Today’s Top 3
3. Active Projects
4. Blocked / Needs Review
5. Quick Capture
6. Collector Health

Question:
- Is this the right order, or should Quick Capture / Active Projects be higher?

### 5. Manual vs Automated Phase 2 Inputs

For Phase 2, decide what starts manual:

Recommended manual-first:
- Today’s Top 3
- Project Registry
- Blocked / Needs Review
- Quick Capture classification

Automated-first:
- Codex Usage
- Collector Health
- Codex historical aggregates, if added

Question:
- Is manual-first acceptable for project/task cards until automation is ready?

### 6. Project Categories and Initial Projects

Confirm the initial project groups:

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

Question:
- Should any be added, renamed, merged, or hidden for v1?

### 7. Visual Direction for Phase 2

Confirm the Phase 2 UI direction:

- dark mode first
- purple/violet/cobalt glow
- glass-card look
- desktop-first responsive layout
- fixed card layout before draggable grid

Question:
- Do we build clean/simple first, or spend more time on the premium futuristic look during Phase 2?

### 8. Collector Cadence

Question:
- Should Phase 2 keep collector runs manual, or add a safe scheduled collector after the manual collector proves stable?

Recommended default:
- Add scheduled collection only after manual runs are stable and logs are clean.

### 9. Top 3 Workflow

Questions:
- Should Today’s Top 3 reset daily or carry forward until completed?
- Should each Top 3 item require a project?
- Should completed items stay visible for the day?

Recommended default:
- Carry forward until completed.
- Project optional.
- Completed items stay visible but collapsed/faded for the day.

### 10. Phase 2 Stop Point

Question:
- Should Phase 2 stop as soon as the Daily dashboard is useful, or keep going until Codex historical aggregates are also added?

Recommended default:
- Stop when the Daily dashboard is useful.
- Treat Codex historical aggregates as Phase 2 bonus, not a blocker.

### Phase 2 Start Criteria

Start Phase 2 only when:
- Phase 1 Definition of Done is met.
- Safety check passes.
- Project registry model is chosen.
- Daily card order is chosen.
- Manual-vs-automated inputs are agreed.
- The Phase 2 stop point is clear.


## Phase 2 Plan

Phase 2 should expand the working Phase 1 slice into a useful daily dashboard, without trying to build the entire long-term system.

Phase 2 target:

```txt
Daily Command Center v1
```

Phase 2 starts only after Phase 1 is working:
- backend starts
- Codex collector runs safely
- SQLite stores sanitized data
- API returns Codex usage
- one frontend Codex Usage card displays real data
- startup/run support exists

### Phase 2 Goals

1. Turn the single-card proof into a small daily dashboard.
2. Add basic project/task context so AI usage is connected to actual work.
3. Add stale/fresh data handling across cards.
4. Add manual fallback/correction only where automation is not ready yet.
5. Keep the system local-first and safe.

### Phase 2 Build Order

#### 1. Daily Dashboard Shell

Create the first real dashboard page:

```txt
Daily
```

Cards:
- Codex Usage
- Today’s Top 3
- Active Projects
- Blocked / Needs Review
- Quick Capture
- Collector Health

Keep layout simple:
- fixed card layout first
- no draggable/resizable grid yet
- no full customization yet

#### 2. Project Registry v1

Add a local project registry table/file.

Fields:
- `project_key`
- `project_label`
- `parent_project`
- `status`
- `priority`
- `default_ai_tool`
- `safe_notes`
- `created_at`
- `updated_at`

Statuses:
- Active
- Paused
- Someday
- Archived
- Blocked
- Needs Review

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

#### 3. Quick Capture v1

Add a simple capture box.

Purpose:
- catch ideas, tasks, bugs, reminders, and unsorted notes quickly

Fields:
- text
- captured_at
- optional project label
- optional status
- optional type
- processed flag

Rules:
- Do not overbuild classification yet.
- Store as local text rows.
- Add review workflow later.

#### 4. Today’s Top 3 v1

Add a basic manually editable Top 3 list.

Fields:
- title
- project
- reason
- status
- created_at
- completed_at

Rules:
- Start manual.
- Recommendation/scoring can come later.
- Keep it easy to override.

#### 5. Collector Health v1

Show basic health for collectors:
- last successful run
- last failed run
- latest status
- records written
- safe error message
- freshness badge

Collectors tracked in Phase 2:
- Codex live usage collector
- Codex local historical collector if added during Phase 2
- any placeholder/manual collectors should be clearly marked manual or unavailable

#### 6. Codex Historical Usage Collector

Add local historical Codex aggregate collector after live usage is stable.

Use only sanitized aggregate data:
- session count by day/week
- token trend by day/week
- model breakdown
- safe project-label breakdown

Do not ingest/display:
- prompt previews
- first user messages
- raw logs
- raw rollout files
- full workspace paths

#### 7. Basic Frontend Polish

Add:
- dark mode
- purple/violet/cobalt glow direction
- glass-card look
- clear stale/fresh/confidence badges
- responsive enough for desktop first

Mobile polish waits until later.

### Phase 2 Definition of Done

Phase 2 is done when:
- Daily page loads locally.
- Codex Usage card still works.
- Today’s Top 3 card works.
- Active Projects card reads from local project registry.
- Quick Capture can save entries.
- Collector Health card shows real collector run status.
- Data freshness badges are visible.
- Codex historical aggregates are available or explicitly deferred.
- No secrets or raw sensitive data are stored/displayed/exported.

### Phase 2 Non-Goals

Do not build yet:
- full Weekly/Monthly pages
- project recommendation engine
- AI “best tool right now” scoring
- Claude/ChatGPT collectors unless very easy
- draggable/resizable grid
- full mobile/PWA install polish
- notifications/reminders
- calendar/email integrations
- full automation scheduler UI
- external hosting
- multi-user login

### Phase 2 Immediate Next Decision

Before implementation of Phase 2, decide whether the project registry should start as:

```txt
Option A: SQLite table only
Option B: Markdown/JSON project files + SQLite index
```

Recommended:
Start with SQLite table plus optional exported Markdown later.


## Implementation Backlog

- Build the safe Codex live-usage collector using sanitized `/wham/usage` snapshots.
- Start with user-triggered collection.
- Add scheduled/local collection only after user-triggered collection is working safely.
- Build local Codex historical usage collector from sanitized SQLite aggregates.
- Add account grouping by `account_key_hash`.
- Add safe project labeling and project-key hashing.
- Add manual correction/fallback form after automated collectors exist.

## Open Questions

Keep these unresolved decisions tracked:

- Clarify Codex `tokens_used` semantics across models, cache, context, and reasoning.
- Define the AI usefulness/output-quality scoring scale.
- Confirm exact subscription plans/reset rules for ChatGPT, Claude, Claude Cowork, Claude Design, and any non-Codex sources.
- Verify Claude Code local logs and how Claude Cowork / Claude Design map to tracked tools.
- Decide dashboard name.
- Decide final tech stack/backend layer.
- Decide script schedule format.
- Decide pinned default projects.
- Decide exact project categories and project-to-tool preference mapping.
- Decide manual fallback/correction form details.
- Decide Top 3 scoring weights.
- Decide Daily view card priority/order defaults.
- Decide default landing view.
- Decide default project icons and card size presets.


## Resolved Decisions / No Longer Open

- `/wham/usage` endpoint discovery is resolved.
- Local dashboard collector capability for live Codex usage is confirmed.
- Codex live 5-hour and weekly meters are collectable.
- Codex live quota source and field mapping are confirmed; remaining work is implementation, not discovery.
- Codex account identity can be separated safely using a stable hashed subject/account key plus a local-only display label.
- Multi-subscription account separation is possible.
- `account_key_hash` is the canonical account grouping field.
- Account labels and names are local display fields.
- Raw project paths should not be stored/displayed by default.
- Screenshot/OCR is not needed for Codex usage values.
- Deep reverse engineering of the VS Code extension host is no longer needed unless the direct collector fails.
- Provider-neutral `session_count` should be supported.


## Confirmed Codex Quota Snapshot Fields

A Codex live quota snapshot should include:

```json
{
  "provider": "openai",
  "tool": "codex",
  "account_key_hash": "sha256_of_stable_subject",
  "account_label": "local_display_email_or_label",
  "account_name": "local_display_name_optional",
  "plan_type": "plus_or_other",
  "reset_credits_available": null,
  "quota_5h_used_percent": null,
  "quota_5h_remaining_percent": null,
  "quota_5h_reset_at": null,
  "quota_weekly_used_percent": null,
  "quota_weekly_remaining_percent": null,
  "quota_weekly_reset_at": null,
  "collected_at": "timestamp",
  "source_type": "official_endpoint",
  "source_label": "chatgpt_backend_wham_usage",
  "confidence": "high",
  "freshness": "fresh"
}
```

Rules:
- Store only sanitized fields.
- Do not store raw endpoint payloads in the dashboard database or exports.
- Temporary raw endpoint debugging, if ever needed, must be manually enabled, local-only, short-lived, and must never include raw tokens, cookies, authorization headers, or auth file contents.
- Do not store raw tokens or authorization headers.
- `account_key_hash` is canonical for grouping multiple subscriptions.
- `account_label` is for local display only.
