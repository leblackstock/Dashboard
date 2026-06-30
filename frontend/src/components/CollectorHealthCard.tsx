import { Activity, AlertTriangle, CheckCircle2 } from "lucide-react";
import type { CollectorHealthItem } from "../lib/types";
import { DashboardCard } from "./DashboardCard";
import { Badge } from "./ui/badge";

function freshnessTone(freshness: string) {
  if (freshness === "fresh") return "fresh";
  if (freshness === "slightly_stale") return "warn";
  if (freshness === "stale" || freshness === "very_stale") return "stale";
  return "neutral";
}

function statusIcon(status: string) {
  if (status === "success") {
    return <CheckCircle2 className="h-4 w-4 text-mint" aria-hidden="true" />;
  }
  if (status === "failed") {
    return <AlertTriangle className="h-4 w-4 text-amber" aria-hidden="true" />;
  }
  return <Activity className="h-4 w-4 text-cobalt" aria-hidden="true" />;
}

function statusIconShell(status: string) {
  if (status === "success") {
    return "border-mint/40 bg-mint/10";
  }
  if (status === "failed") {
    return "border-amber/40 bg-amber/10";
  }
  return "border-cobalt/40 bg-cobalt/10";
}

function formatDate(value: string | null) {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "—";
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit"
  }).format(date);
}

export function CollectorHealthCard({ collectors }: { collectors: CollectorHealthItem[] }) {
  return (
    <DashboardCard title="Collector Health" eyebrow="Freshness">
      <div className="space-y-3">
        {collectors.length === 0 ? (
          <p className="dashboard-soft-panel rounded-lg border p-3 text-sm text-muted">
            No collectors tracked.
          </p>
        ) : (
          collectors.map((collector) => (
            <div
              key={collector.collector_name}
              className="dashboard-soft-panel rounded-lg border p-3"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <div className="flex items-start gap-3">
                    <span
                      className={`inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-md border ${statusIconShell(
                        collector.latest_status
                      )}`}
                    >
                      {statusIcon(collector.latest_status)}
                    </span>
                    <div className="min-w-0">
                      <p className="break-words text-sm font-semibold text-ink">
                        {collector.label}
                      </p>
                      <p className="mt-1 text-xs text-muted">
                        Last success {formatDate(collector.last_success_at)}
                      </p>
                      {collector.last_failed_at ? (
                        <p className="mt-1 text-xs text-amber">
                          Last failure {formatDate(collector.last_failed_at)}
                        </p>
                      ) : null}
                    </div>
                  </div>
                </div>
                <div className="flex shrink-0 flex-col items-end gap-2">
                  <Badge tone={freshnessTone(collector.freshness)}>
                    {collector.freshness}
                  </Badge>
                  <Badge tone="neutral">{collector.latest_status}</Badge>
                </div>
              </div>
              <div className="mt-3 grid gap-2 text-xs text-muted sm:grid-cols-[0.8fr_1.2fr]">
                <div className="rounded-md border border-line/60 bg-bg/25 p-2.5 shadow-[inset_0_1px_0_rgb(255_255_255_/_0.025)]">
                  <p className="font-medium">Records</p>
                  <p className="mt-1 text-sm font-semibold text-ink">
                    {collector.records_written}
                  </p>
                </div>
                <div className="rounded-md border border-line/60 bg-bg/25 p-2.5 shadow-[inset_0_1px_0_rgb(255_255_255_/_0.025)]">
                  <p className="font-medium">Status</p>
                  <p className="mt-1 break-words text-sm font-semibold text-ink">
                    {collector.safe_message}
                  </p>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </DashboardCard>
  );
}
