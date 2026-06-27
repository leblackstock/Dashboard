import type {
  BlockedItem,
  BlockedItemCreate,
  BlockedItemUpdate,
  CodexUsageResponse,
  DailyDashboardResponse,
  Project,
  ProjectCreate,
  QuickCapture,
  QuickCaptureCreate,
  TopItem,
  TopItemCreate,
  TopItemUpdate
} from "./types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers
    }
  });
  if (!response.ok) {
    throw new Error("dashboard_api_request_failed");
  }
  return (await response.json()) as T;
}

export async function fetchCodexUsage(): Promise<CodexUsageResponse> {
  return request<CodexUsageResponse>("/api/ai/codex/live-usage");
}

export async function fetchDailyDashboard(): Promise<DailyDashboardResponse> {
  return request<DailyDashboardResponse>("/api/daily");
}

export async function createProject(payload: ProjectCreate): Promise<Project> {
  return request<Project>("/api/projects", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export async function createTopItem(payload: TopItemCreate): Promise<TopItem> {
  return request<TopItem>("/api/top-items", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export async function updateTopItem(id: number, payload: TopItemUpdate): Promise<TopItem> {
  return request<TopItem>(`/api/top-items/${id}`, {
    method: "PATCH",
    body: JSON.stringify(payload)
  });
}

export async function createQuickCapture(
  payload: QuickCaptureCreate
): Promise<QuickCapture> {
  return request<QuickCapture>("/api/quick-captures", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export async function createBlockedItem(payload: BlockedItemCreate): Promise<BlockedItem> {
  return request<BlockedItem>("/api/blocked-items", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export async function updateBlockedItem(
  id: number,
  payload: BlockedItemUpdate
): Promise<BlockedItem> {
  return request<BlockedItem>(`/api/blocked-items/${id}`, {
    method: "PATCH",
    body: JSON.stringify(payload)
  });
}
