import { useQuery } from "@tanstack/react-query";
import { RefreshCcw, RotateCcw } from "lucide-react";
import { useEffect, useState } from "react";
import { fetchDailyDashboard } from "../lib/api";
import { ActiveProjectsCard } from "./ActiveProjectsCard";
import { BlockedReviewCard } from "./BlockedReviewCard";
import { CodexUsageCard } from "./CodexUsageCard";
import { CollectorHealthCard } from "./CollectorHealthCard";
import {
  DASHBOARD_LAYOUT_STORAGE_KEY,
  DEFAULT_DASHBOARD_CARD_ORDER,
  DraggableDashboardGrid,
  loadDashboardCardOrder,
  saveDashboardCardOrder
} from "./DraggableDashboardGrid";
import { QuickCaptureCard } from "./QuickCaptureCard";
import { TodaysTop3Card } from "./TodaysTop3Card";

export function DailyDashboard() {
  const [cardOrder, setCardOrder] = useState(loadDashboardCardOrder);
  const [layoutStatus, setLayoutStatus] = useState("");
  const query = useQuery({
    queryKey: ["daily-dashboard"],
    queryFn: fetchDailyDashboard
  });

  const projects = query.data?.projects ?? [];
  const topItems = query.data?.top_items ?? [];
  const briefSuggestions = query.data?.brief_suggestions ?? [];
  const blockedItems = query.data?.blocked_items ?? [];
  const quickCaptures = query.data?.quick_captures ?? [];
  const collectorHealth = query.data?.collector_health ?? [];
  const isDefaultLayout =
    cardOrder.length === DEFAULT_DASHBOARD_CARD_ORDER.length &&
    cardOrder.every((cardId, index) => cardId === DEFAULT_DASHBOARD_CARD_ORDER[index]);

  useEffect(() => {
    if (!layoutStatus) return;
    const timeout = window.setTimeout(() => setLayoutStatus(""), 2500);
    return () => window.clearTimeout(timeout);
  }, [layoutStatus]);

  function updateCardOrder(nextOrder: typeof cardOrder) {
    setCardOrder(nextOrder);
    saveDashboardCardOrder(nextOrder);
    setLayoutStatus("");
  }

  function resetCardOrder() {
    if (isDefaultLayout) return;
    window.localStorage.removeItem(DASHBOARD_LAYOUT_STORAGE_KEY);
    setCardOrder([...DEFAULT_DASHBOARD_CARD_ORDER]);
    setLayoutStatus("Layout reset.");
  }

  return (
    <div className="mx-auto w-full max-w-7xl">
      <header className="mb-6 flex flex-col gap-4 border-b border-line pb-5 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-[0.18em] text-cobalt">
            Daily
          </p>
          <h1 className="mt-2 text-3xl font-semibold text-ink">Daily Command Center</h1>
        </div>
        <div className="flex flex-wrap items-center justify-end gap-2">
          <span className="min-w-[76px] text-right text-xs text-muted" aria-live="polite">
            {layoutStatus}
          </span>
          <button
            className="inline-flex h-10 w-10 items-center justify-center rounded-md border border-line bg-surface text-muted transition hover:border-cobalt hover:text-ink disabled:cursor-not-allowed disabled:opacity-40"
            disabled={isDefaultLayout}
            onClick={resetCardOrder}
            type="button"
            title={isDefaultLayout ? "Dashboard layout is already at default" : "Reset dashboard layout"}
            aria-label="Reset dashboard layout"
          >
            <RotateCcw className="h-4 w-4" aria-hidden="true" />
          </button>
          <button
            className="inline-flex h-10 w-10 items-center justify-center rounded-md border border-line bg-surface text-muted transition hover:border-cobalt hover:text-ink disabled:opacity-50"
            disabled={query.isFetching}
            onClick={() => void query.refetch()}
            type="button"
            title="Refresh"
            aria-label="Refresh"
          >
            <RefreshCcw className="h-4 w-4" aria-hidden="true" />
          </button>
        </div>
      </header>

      {query.isLoading ? (
        <div className="rounded-lg border border-line bg-panel px-5 py-4 text-sm text-muted">
          Loading…
        </div>
      ) : query.isError ? (
        <div className="rounded-lg border border-red-400/40 bg-red-400/10 px-5 py-4 text-sm text-red-200">
          Unable to load Daily dashboard.
        </div>
      ) : null}

      <DraggableDashboardGrid
        cards={{
          "codex-usage": {
            label: "Codex Usage",
            content: <CodexUsageCard />
          },
          "todays-top3": {
            label: "Today’s Top 3",
            content: (
              <TodaysTop3Card
                briefSuggestions={briefSuggestions}
                items={topItems}
                projects={projects}
              />
            )
          },
          "active-projects": {
            label: "Active Projects",
            content: <ActiveProjectsCard projects={projects} />
          },
          "blocked-review": {
            label: "Blocked / Needs Review",
            content: <BlockedReviewCard items={blockedItems} projects={projects} />
          },
          "quick-capture": {
            label: "Quick Capture",
            content: <QuickCaptureCard captures={quickCaptures} projects={projects} />
          },
          "collector-health": {
            label: "Collector Health",
            content: <CollectorHealthCard collectors={collectorHealth} />
          }
        }}
        onOrderChange={updateCardOrder}
        order={cardOrder}
      />
    </div>
  );
}
