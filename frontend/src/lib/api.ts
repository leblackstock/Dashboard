import type {
  BriefSuggestion,
  BriefSuggestionsImportResponse,
  BlockedItem,
  BlockedItemCreate,
  BlockedItemUpdate,
  CodexCollectResponse,
  CodexUsageResponse,
  DailyDashboardResponse,
  Project,
  ProjectCreate,
  QuickCapture,
  QuickCaptureCreate,
  TopItem,
  TopItemCreate,
  TopItemPlacementResponse,
  TopItemsResponse,
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
    let safeCode = "dashboard_api_request_failed";
    try {
      const payload = (await response.json()) as { detail?: unknown };
      if (
        typeof payload.detail === "string" &&
        /^[a-z0-9_]+$/.test(payload.detail)
      ) {
        safeCode = payload.detail;
      }
    } catch {
      // Keep the generic safe code when the response is not JSON.
    }
    throw new DashboardApiError(safeCode);
  }
  return (await response.json()) as T;
}

export class DashboardApiError extends Error {
  constructor(public readonly safeCode: string) {
    super("dashboard_api_request_failed");
  }
}

export async function fetchCodexUsage(): Promise<CodexUsageResponse> {
  return request<CodexUsageResponse>("/api/ai/codex/live-usage");
}

export async function collectCodexUsage(): Promise<CodexCollectResponse> {
  return request<CodexCollectResponse>("/api/ai/codex/collect", {
    method: "POST",
    body: JSON.stringify({})
  });
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

export async function createTopItem(
  payload: TopItemCreate
): Promise<TopItemPlacementResponse> {
  return request<TopItemPlacementResponse>("/api/top-items", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export async function reorderTopItems(itemIds: number[]): Promise<TopItemsResponse> {
  return request<TopItemsResponse>("/api/top-items/reorder", {
    method: "PUT",
    body: JSON.stringify({ item_ids: itemIds })
  });
}

export async function promoteTopItem(id: number): Promise<TopItemPlacementResponse> {
  return request<TopItemPlacementResponse>(`/api/top-items/${id}/promote`, {
    method: "POST",
    body: JSON.stringify({})
  });
}

export async function removeTopItem(id: number): Promise<TopItem> {
  return request<TopItem>(`/api/top-items/${id}/remove`, {
    method: "POST",
    body: JSON.stringify({})
  });
}

export async function returnTopItemToSuggestions(id: number): Promise<TopItem> {
  return request<TopItem>(`/api/top-items/${id}/return-to-suggestions`, {
    method: "POST",
    body: JSON.stringify({})
  });
}

export async function updateTopItem(id: number, payload: TopItemUpdate): Promise<TopItem> {
  return request<TopItem>(`/api/top-items/${id}`, {
    method: "PATCH",
    body: JSON.stringify(payload)
  });
}

export async function importBriefSuggestions(): Promise<BriefSuggestionsImportResponse> {
  return request<BriefSuggestionsImportResponse>("/api/brief-suggestions/import", {
    method: "POST",
    body: JSON.stringify({})
  });
}

export async function acceptBriefSuggestion(
  id: number
): Promise<TopItemPlacementResponse> {
  return request<TopItemPlacementResponse>(`/api/brief-suggestions/${id}/accept`, {
    method: "POST",
    body: JSON.stringify({})
  });
}

export async function ignoreBriefSuggestion(id: number): Promise<BriefSuggestion> {
  return request<BriefSuggestion>(`/api/brief-suggestions/${id}/ignore`, {
    method: "POST",
    body: JSON.stringify({})
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
