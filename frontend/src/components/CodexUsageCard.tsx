import { useQuery } from "@tanstack/react-query";
import { Clock3, RefreshCcw, ShieldCheck, Zap } from "lucide-react";
import { fetchCodexUsage } from "../lib/api";
import type { CodexUsageAccount, QuotaWindow } from "../lib/types";
import { Badge } from "./ui/badge";
import { Card, CardContent, CardHeader } from "./ui/card";
import { Progress } from "./ui/progress";

function freshnessTone(freshness: string) {
  if (freshness === "fresh") return "fresh";
  if (freshness === "slightly_stale") return "warn";
  if (freshness === "stale" || freshness === "very_stale") return "stale";
  return "neutral";
}

function formatPercent(value: number | null) {
  if (value == null) return "—";
  return `${Math.round(value)}%`;
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

function formatCountdown(value: string | null) {
  if (!value) return "—";
  const resetAt = new Date(value).getTime();
  if (Number.isNaN(resetAt)) return "—";
  const diffMs = resetAt - Date.now();
  if (diffMs <= 0) return "Ready";
  const totalMinutes = Math.ceil(diffMs / 60_000);
  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;
  if (hours >= 24) return `${Math.floor(hours / 24)}d ${hours % 24}h`;
  if (hours > 0) return `${hours}h ${minutes}m`;
  return `${minutes}m`;
}

function UsageWindow({ label, quota }: { label: string; quota: QuotaWindow }) {
  return (
    <div className="space-y-3 rounded-lg border border-line bg-surface p-4">
      <div className="flex items-center justify-between gap-3">
        <span className="text-sm font-medium text-ink">{label}</span>
        <span className="text-sm text-muted">{formatPercent(quota.remaining_percent)} left</span>
      </div>
      <Progress value={quota.used_percent} />
      <div className="flex items-center justify-between gap-3 text-xs text-muted">
        <span>{formatPercent(quota.used_percent)} used</span>
        <span>Reset {formatCountdown(quota.reset_at)}</span>
      </div>
    </div>
  );
}

function AccountUsage({ account }: { account: CodexUsageAccount }) {
  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-sm text-muted">{account.account_label ?? "Codex account"}</p>
          <h2 className="mt-1 text-2xl font-semibold text-ink">Codex Usage</h2>
        </div>
        <div className="flex flex-wrap gap-2">
          <Badge tone={freshnessTone(account.freshness)}>{account.freshness}</Badge>
          <Badge tone="neutral">{account.confidence}</Badge>
        </div>
      </div>

      <div className="grid gap-3 sm:grid-cols-3">
        <div className="rounded-lg border border-line bg-surface p-4">
          <div className="flex items-center gap-2 text-muted">
            <ShieldCheck className="h-4 w-4 text-mint" aria-hidden="true" />
            <span className="text-xs">Plan</span>
          </div>
          <p className="mt-2 text-lg font-semibold text-ink">{account.plan_type ?? "Unknown"}</p>
        </div>
        <div className="rounded-lg border border-line bg-surface p-4">
          <div className="flex items-center gap-2 text-muted">
            <Zap className="h-4 w-4 text-amber" aria-hidden="true" />
            <span className="text-xs">Reset credits</span>
          </div>
          <p className="mt-2 text-lg font-semibold text-ink">
            {account.reset_credits_available ?? "—"}
          </p>
        </div>
        <div className="rounded-lg border border-line bg-surface p-4">
          <div className="flex items-center gap-2 text-muted">
            <Clock3 className="h-4 w-4 text-cobalt" aria-hidden="true" />
            <span className="text-xs">Collected</span>
          </div>
          <p className="mt-2 text-lg font-semibold text-ink">
            {formatDate(account.collected_at)}
          </p>
        </div>
      </div>

      <div className="grid gap-3 md:grid-cols-2">
        <UsageWindow label="5-hour quota" quota={account.quota_5h} />
        <UsageWindow label="Weekly quota" quota={account.quota_weekly} />
      </div>
    </div>
  );
}

export function CodexUsageCard() {
  const query = useQuery({
    queryKey: ["codex-usage"],
    queryFn: fetchCodexUsage
  });
  const account = query.data?.accounts[0];

  return (
    <Card className="w-full">
      <CardHeader className="flex flex-row items-center justify-between gap-3">
        <div>
          <p className="text-xs font-medium uppercase text-muted">OpenAI</p>
          <h1 className="mt-1 text-xl font-semibold text-ink">Codex Usage</h1>
        </div>
        <button
          className="inline-flex h-9 w-9 items-center justify-center rounded-md border border-line bg-surface text-muted transition hover:border-cobalt hover:text-ink"
          onClick={() => void query.refetch()}
          type="button"
          title="Refresh"
          aria-label="Refresh"
        >
          <RefreshCcw className="h-4 w-4" aria-hidden="true" />
        </button>
      </CardHeader>
      <CardContent>
        {query.isLoading ? (
          <p className="text-sm text-muted">Loading…</p>
        ) : query.isError ? (
          <p className="text-sm text-red-200">Unable to load Codex usage.</p>
        ) : account ? (
          <AccountUsage account={account} />
        ) : (
          <p className="text-sm text-muted">No Codex usage snapshot yet.</p>
        )}
      </CardContent>
    </Card>
  );
}
