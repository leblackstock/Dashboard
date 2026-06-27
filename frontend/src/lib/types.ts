export type QuotaWindow = {
  used_percent: number | null;
  remaining_percent: number | null;
  reset_at: string | null;
};

export type CodexUsageAccount = {
  account_key_hash: string;
  account_label: string | null;
  account_name: string | null;
  plan_type: string | null;
  reset_credits_available: number | null;
  quota_5h: QuotaWindow;
  quota_weekly: QuotaWindow;
  freshness: string;
  confidence: string;
  collected_at: string;
};

export type CodexUsageResponse = {
  accounts: CodexUsageAccount[];
};
