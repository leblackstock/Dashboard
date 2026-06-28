import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Clock3, RefreshCcw, ShieldCheck, Zap } from "lucide-react";
import { useState } from "react";
import { collectCodexUsage, fetchCodexUsage } from "../lib/api";
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
  if (value == null) return "Unavailable";
  return `${Math.round(value)}%`;
}

function formatDate(value: string | null) {
  if (!value) return "Unavailable";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Unavailable";
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit"
  }).format(date);
}

function formatCountdown(value: string | null) {
  if (!value) return null;
  const resetAt = new Date(value).getTime();
  if (Number.isNaN(resetAt)) return null;
  const diffMs = resetAt - Date.now();
  if (diffMs <= 0) return "ready";
  const totalMinutes = Math.ceil(diffMs / 60_000);
  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;
  if (hours >= 24) return `${Math.floor(hours / 24)}d ${hours % 24}h`;
  if (hours > 0) return `${hours}h ${minutes}m`;
  return `${minutes}m`;
}

function formatResetClock(value: string | null, includeWeekday: boolean) {
  if (!value) return null;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return null;
  const formatted = new Intl.DateTimeFormat(undefined, {
    timeZone: "America/New_York",
    weekday: includeWeekday ? "short" : undefined,
    hour: "numeric",
    minute: "2-digit"
  }).format(date);
  return `${formatted} ET`;
}

function UsageWindow({
  label,
  quota,
  includeResetWeekday = false
}: {
  label: string;
  quota: QuotaWindow;
  includeResetWeekday?: boolean;
}) {
  const remainingLabel =
    quota.remaining_percent == null ? "Unavailable" : `${formatPercent(quota.remaining_percent)} left`;
  const usedLabel =
    quota.used_percent == null ? "Used unavailable" : `${formatPercent(quota.used_percent)} used`;
  const resetCountdown = formatCountdown(quota.reset_at);
  const resetClock = formatResetClock(quota.reset_at, includeResetWeekday);
  return (
    <div className="space-y-3 rounded-lg border border-line bg-surface p-4">
      <div className="flex items-center justify-between gap-3">
        <span className="text-sm font-medium text-ink">{label}</span>
        <span className="text-sm text-muted">{remainingLabel}</span>
      </div>
      <Progress value={quota.used_percent} />
      <div className="flex items-start justify-between gap-3 text-xs text-muted">
        <span>{usedLabel}</span>
        {resetCountdown && resetClock ? (
          <span className="flex flex-col items-end gap-1 text-right">
            <span>{resetCountdown === "ready" ? "Reset ready" : `Reset in ${resetCountdown}`}</span>
            <span>Resets at {resetClock}</span>
          </span>
        ) : (
          <span>Reset Unavailable</span>
        )}
      </div>
    </div>
  );
}

function AccountUsage({
  account,
  accountLabel
}: {
  account: CodexUsageAccount;
  accountLabel: string;
}) {
  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-sm text-muted">{accountLabel}</p>
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
            {account.reset_credits_available ?? "Unavailable"}
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
        <UsageWindow
          label="Weekly quota"
          quota={account.quota_weekly}
          includeResetWeekday
        />
      </div>
    </div>
  );
}

function accountBaseLabel(account: CodexUsageAccount) {
  const candidates = [account.account_label?.trim(), account.account_name?.trim()].filter(
    (value): value is string => Boolean(value)
  );
  const emailLabel = candidates.find((candidate) => candidate.indexOf("@") > 0);
  if (emailLabel) return emailLabel.slice(0, emailLabel.indexOf("@"));

  return (
    candidates.find((candidate) => !/^codex account(?: \d+)?$/i.test(candidate)) ?? null
  );
}

function accountDisplayLabels(accounts: CodexUsageAccount[]) {
  const baseLabels = accounts.map(accountBaseLabel);
  const totals = new Map<string, number>();

  for (const label of baseLabels) {
    if (!label) continue;
    const key = label.toLocaleLowerCase();
    totals.set(key, (totals.get(key) ?? 0) + 1);
  }

  let fallbackIndex = 0;
  return baseLabels.map((label) => {
    if (!label) return `Codex account ${++fallbackIndex}`;
    const key = label.toLocaleLowerCase();
    if ((totals.get(key) ?? 0) === 1) return label;
    return `Codex account ${++fallbackIndex}`;
  });
}

export function CodexUsageCard() {
  const queryClient = useQueryClient();
  const [selectedAccountKey, setSelectedAccountKey] = useState<string | null>(null);
  const query = useQuery({
    queryKey: ["codex-usage"],
    queryFn: fetchCodexUsage
  });
  const collectMutation = useMutation({
    mutationFn: collectCodexUsage,
    onSuccess: (result) => {
      if (result.status === "success") {
        void queryClient.invalidateQueries({ queryKey: ["codex-usage"] });
      }
      void queryClient.invalidateQueries({ queryKey: ["daily-dashboard"] });
    }
  });
  const accounts = query.data?.accounts ?? [];
  const displayLabels = accountDisplayLabels(accounts);
  const account =
    accounts.find((candidate) => candidate.account_key_hash === selectedAccountKey) ??
    accounts[0];
  const selectedAccountIndex = account
    ? accounts.findIndex((candidate) => candidate.account_key_hash === account.account_key_hash)
    : -1;
  const selectedAccountLabel = displayLabels[selectedAccountIndex] ?? "Codex account";
  const lastUpdated = account?.collected_at ?? collectMutation.data?.last_updated ?? null;
  const collectFailed = collectMutation.data?.status === "failed" || collectMutation.isError;
  const collectMessage = collectMutation.isPending
    ? "Collecting…"
    : collectFailed
      ? accounts.length > 0
        ? "Refresh failed. Showing last saved Codex usage."
        : collectMutation.data?.message ?? "Codex usage could not be refreshed. Try again later."
      : collectMutation.data?.message;

  return (
    <Card className="w-full">
      <CardHeader className="flex flex-row flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-xs font-medium uppercase text-muted">OpenAI</p>
          <h1 className="mt-1 text-xl font-semibold text-ink">Codex Usage</h1>
        </div>
        <button
          className="inline-flex h-9 items-center justify-center gap-2 rounded-md border border-line bg-surface px-3 text-sm text-muted transition hover:border-cobalt hover:text-ink disabled:cursor-not-allowed disabled:opacity-60"
          disabled={collectMutation.isPending}
          onClick={() => collectMutation.mutate()}
          type="button"
          title="Refresh Codex Usage"
        >
          <RefreshCcw
            className={`h-4 w-4 ${collectMutation.isPending ? "animate-spin" : ""}`}
            aria-hidden="true"
          />
          <span>Refresh Codex Usage</span>
        </button>
      </CardHeader>
      <CardContent>
        <div className="mb-4 flex flex-wrap items-center gap-2">
          {collectMessage ? (
            <span
              className={`rounded-md border px-3 py-2 text-sm ${
                collectFailed
                  ? "border-red-400/40 bg-red-400/10 text-red-200"
                  : collectMutation.isPending
                    ? "border-amber/40 bg-amber/10 text-amber"
                    : "border-mint/40 bg-mint/10 text-mint"
              }`}
            >
              {collectMessage}
            </span>
          ) : null}
          {lastUpdated ? <Badge tone="neutral">Last updated {formatDate(lastUpdated)}</Badge> : null}
        </div>
        {accounts.length > 1 ? (
          <div className="mb-5 flex flex-wrap gap-2" aria-label="Codex accounts">
            {accounts.map((candidate, index) => {
              const selected = candidate.account_key_hash === account?.account_key_hash;
              return (
                <button
                  aria-pressed={selected}
                  className={`rounded-md border px-3 py-2 text-left transition ${
                    selected
                      ? "border-cobalt bg-cobalt/15 text-ink"
                      : "border-line bg-surface text-muted hover:border-cobalt/70 hover:text-ink"
                  }`}
                  key={candidate.account_key_hash}
                  onClick={() => {
                    setSelectedAccountKey(candidate.account_key_hash);
                    collectMutation.reset();
                  }}
                  type="button"
                  title={displayLabels[index]}
                >
                  <span className="block max-w-[180px] truncate text-sm font-medium">
                    {displayLabels[index]}
                  </span>
                </button>
              );
            })}
          </div>
        ) : null}
        {query.isLoading ? (
          <p className="text-sm text-muted">Loading…</p>
        ) : query.isError ? (
          <p className="text-sm text-red-200">Unable to load Codex usage.</p>
        ) : account ? (
          <AccountUsage account={account} accountLabel={selectedAccountLabel} />
        ) : (
          <p className="text-sm text-muted">No Codex usage snapshot yet.</p>
        )}
      </CardContent>
    </Card>
  );
}
