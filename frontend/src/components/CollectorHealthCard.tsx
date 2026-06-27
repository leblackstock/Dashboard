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
          <p className="text-sm text-muted">No collectors tracked.</p>
        ) : (
          collectors.map((collector) => (
            <div
              key={collector.collector_name}
              className="rounded-md border border-line bg-surface p-3"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    {statusIcon(collector.latest_status)}
                    <p className="break-words text-sm font-medium text-ink">{collector.label}</p>
                  </div>
                  <p className="mt-2 text-xs text-muted">
                    Last success {formatDate(collector.last_success_at)}
                  </p>
                  {collector.last_failed_at ? (
                    <p className="mt-1 text-xs text-muted">
                      Last failure {formatDate(collector.last_failed_at)}
                    </p>
                  ) : null}
                </div>
                <div className="flex shrink-0 flex-col items-end gap-2">
                  <Badge tone={freshnessTone(collector.freshness)}>
                    {collector.freshness}
                  </Badge>
                  <Badge tone="neutral">{collector.latest_status}</Badge>
                </div>
              </div>
              <div className="mt-3 grid grid-cols-2 gap-2 text-xs text-muted">
                <div className="rounded-md border border-line bg-panel/70 p-2">
                  <p>Records</p>
                  <p className="mt-1 text-sm font-semibold text-ink">
                    {collector.records_written}
                  </p>
                </div>
                <div className="rounded-md border border-line bg-panel/70 p-2">
                  <p>Status</p>
                  <p className="mt-1 truncate text-sm font-semibold text-ink">
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
