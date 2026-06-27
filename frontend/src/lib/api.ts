import type { CodexUsageResponse } from "./types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export async function fetchCodexUsage(): Promise<CodexUsageResponse> {
  const response = await fetch(`${API_BASE_URL}/api/ai/codex/live-usage`);
  if (!response.ok) {
    throw new Error("codex_usage_request_failed");
  }
  return (await response.json()) as CodexUsageResponse;
}
