import { useQuery } from "@tanstack/react-query";
import { RefreshCcw } from "lucide-react";
import { fetchDailyDashboard } from "../lib/api";
import { ActiveProjectsCard } from "./ActiveProjectsCard";
import { BlockedReviewCard } from "./BlockedReviewCard";
import { CodexUsageCard } from "./CodexUsageCard";
import { CollectorHealthCard } from "./CollectorHealthCard";
import { QuickCaptureCard } from "./QuickCaptureCard";
import { TodaysTop3Card } from "./TodaysTop3Card";

export function DailyDashboard() {
  const query = useQuery({
    queryKey: ["daily-dashboard"],
    queryFn: fetchDailyDashboard
  });

  const projects = query.data?.projects ?? [];
  const topItems = query.data?.top_items ?? [];
  const blockedItems = query.data?.blocked_items ?? [];
  const quickCaptures = query.data?.quick_captures ?? [];
  const collectorHealth = query.data?.collector_health ?? [];

  return (
    <div className="mx-auto w-full max-w-7xl">
      <header className="mb-6 flex flex-col gap-4 border-b border-line pb-5 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-[0.18em] text-cobalt">
            Daily
          </p>
          <h1 className="mt-2 text-3xl font-semibold text-ink">Daily Command Center</h1>
        </div>
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

      <div className="grid gap-4 xl:grid-cols-12">
        <div className="xl:col-span-7">
          <CodexUsageCard />
        </div>
        <div className="xl:col-span-5">
          <TodaysTop3Card items={topItems} projects={projects} />
        </div>
        <div className="xl:col-span-4">
          <ActiveProjectsCard projects={projects} />
        </div>
        <div className="xl:col-span-4">
          <BlockedReviewCard items={blockedItems} projects={projects} />
        </div>
        <div className="xl:col-span-4">
          <QuickCaptureCard captures={quickCaptures} projects={projects} />
        </div>
        <div className="xl:col-span-12">
          <CollectorHealthCard collectors={collectorHealth} />
        </div>
      </div>
    </div>
  );
}
