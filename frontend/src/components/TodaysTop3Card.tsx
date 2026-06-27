import { useMutation, useQueryClient } from "@tanstack/react-query";
import { CheckCircle2, Plus, RefreshCcw, XCircle } from "lucide-react";
import { FormEvent, useState } from "react";
import {
  acceptBriefSuggestion,
  createTopItem,
  ignoreBriefSuggestion,
  importBriefSuggestions,
  updateTopItem
} from "../lib/api";
import type { BriefSuggestion, Project, TopItem } from "../lib/types";
import { DashboardCard } from "./DashboardCard";
import { Badge } from "./ui/badge";

const inputClass =
  "w-full rounded-md border border-line bg-surface px-3 py-2 text-sm text-ink outline-none transition placeholder:text-muted focus:border-cobalt";

export function TodaysTop3Card({
  briefSuggestions,
  items,
  projects
}: {
  briefSuggestions: BriefSuggestion[];
  items: TopItem[];
  projects: Project[];
}) {
  const queryClient = useQueryClient();
  const [title, setTitle] = useState("");
  const [projectKey, setProjectKey] = useState("");

  const createMutation = useMutation({
    mutationFn: createTopItem,
    onSuccess: () => {
      setTitle("");
      setProjectKey("");
      void queryClient.invalidateQueries({ queryKey: ["daily-dashboard"] });
    }
  });

  const completeMutation = useMutation({
    mutationFn: (id: number) => updateTopItem(id, { status: "completed" }),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["daily-dashboard"] })
  });

  const importMutation = useMutation({
    mutationFn: importBriefSuggestions,
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["daily-dashboard"] })
  });

  const acceptMutation = useMutation({
    mutationFn: acceptBriefSuggestion,
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["daily-dashboard"] })
  });

  const ignoreMutation = useMutation({
    mutationFn: ignoreBriefSuggestion,
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["daily-dashboard"] })
  });

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = title.trim();
    if (!trimmed) return;
    createMutation.mutate({
      title: trimmed,
      project_key: projectKey || null,
      status: "pending"
    });
  }

  const importFailed = importMutation.isError || importMutation.data?.status === "failed";
  const importSummary = importMutation.data
    ? `${importMutation.data.message} Imported ${importMutation.data.imported}, already imported ${importMutation.data.already_imported}, skipped ${importMutation.data.skipped}.`
    : null;

  return (
    <DashboardCard title="Today’s Top 3" eyebrow="Focus">
      <div className="space-y-4">
        <form className="grid gap-2 sm:grid-cols-[1fr_160px_40px]" onSubmit={handleSubmit}>
          <input
            className={inputClass}
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            placeholder="Add priority"
            maxLength={200}
          />
          <select
            className={inputClass}
            value={projectKey}
            onChange={(event) => setProjectKey(event.target.value)}
            aria-label="Project"
          >
            <option value="">No project</option>
            {projects.map((project) => (
              <option key={project.project_key} value={project.project_key}>
                {project.project_label}
              </option>
            ))}
          </select>
          <button
            className="inline-flex h-10 w-10 items-center justify-center rounded-md border border-cobalt/50 bg-cobalt/15 text-ink transition hover:bg-cobalt/25 disabled:opacity-50"
            disabled={createMutation.isPending}
            type="submit"
            title="Add"
            aria-label="Add"
          >
            <Plus className="h-4 w-4" aria-hidden="true" />
          </button>
        </form>

        {createMutation.isError ? (
          <p className="text-sm text-red-200">Unable to add priority.</p>
        ) : null}

        <div className="space-y-2">
          {items.length === 0 ? (
            <p className="text-sm text-muted">No priorities yet.</p>
          ) : (
            items.map((item) => {
              const completedToday = item.display_state === "completed_today";
              return (
                <div
                  key={item.id}
                  className={`rounded-md border border-line bg-surface p-3 transition ${
                    completedToday ? "opacity-55" : ""
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <p
                        className={`break-words text-sm font-medium text-ink ${
                          completedToday ? "line-through" : ""
                        }`}
                      >
                        {item.title}
                      </p>
                      <div className="mt-2 flex flex-wrap gap-2">
                        {item.project_label ? (
                          <Badge tone="neutral">{item.project_label}</Badge>
                        ) : null}
                        {completedToday ? <Badge tone="fresh">done today</Badge> : null}
                      </div>
                    </div>
                    {!completedToday ? (
                      <button
                        className="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-md border border-line text-muted transition hover:border-mint hover:text-mint disabled:opacity-50"
                        disabled={completeMutation.isPending}
                        onClick={() => completeMutation.mutate(item.id)}
                        type="button"
                        title="Complete"
                        aria-label="Complete"
                      >
                        <CheckCircle2 className="h-4 w-4" aria-hidden="true" />
                      </button>
                    ) : null}
                  </div>
                </div>
              );
            })
          )}
        </div>

        <div className="border-t border-line pt-4">
          <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
            <p className="text-sm font-medium text-ink">Suggested from Brief</p>
            <button
              className="inline-flex h-9 items-center justify-center gap-2 rounded-md border border-line bg-surface px-3 text-sm text-muted transition hover:border-cobalt hover:text-ink disabled:opacity-50"
              disabled={importMutation.isPending}
              onClick={() => importMutation.mutate()}
              type="button"
              title="Refresh Brief Suggestions"
            >
              <RefreshCcw
                className={`h-4 w-4 ${importMutation.isPending ? "animate-spin" : ""}`}
                aria-hidden="true"
              />
              <span>Refresh Brief Suggestions</span>
            </button>
          </div>

          {importMutation.isPending ? (
            <p className="mb-3 rounded-md border border-amber/40 bg-amber/10 px-3 py-2 text-sm text-amber">
              Refreshing brief suggestions…
            </p>
          ) : importSummary ? (
            <p
              className={`mb-3 rounded-md border px-3 py-2 text-sm ${
                importFailed
                  ? "border-red-400/40 bg-red-400/10 text-red-200"
                  : "border-mint/40 bg-mint/10 text-mint"
              }`}
            >
              {importSummary}
            </p>
          ) : null}

          <div className="space-y-2">
            {briefSuggestions.length === 0 ? (
              <p className="text-sm text-muted">No brief suggestions.</p>
            ) : (
              briefSuggestions.map((suggestion) => (
                <div
                  key={suggestion.id}
                  className="rounded-md border border-line bg-surface p-3"
                >
                  <div className="flex flex-col gap-3">
                    <div className="min-w-0">
                      <p className="break-words text-sm font-medium text-ink">
                        {suggestion.title}
                      </p>
                      {suggestion.reason ? (
                        <p className="mt-1 break-words text-xs text-muted">
                          {suggestion.reason}
                        </p>
                      ) : null}
                      <div className="mt-2 flex flex-wrap gap-2">
                        <Badge tone="neutral">{suggestion.source_label}</Badge>
                        {suggestion.project_label ? (
                          <Badge tone="neutral">{suggestion.project_label}</Badge>
                        ) : suggestion.project_key ? (
                          <Badge tone="neutral">{suggestion.project_key}</Badge>
                        ) : null}
                        {suggestion.urgency ? (
                          <Badge tone="warn">{suggestion.urgency}</Badge>
                        ) : null}
                        {suggestion.source_status ? (
                          <Badge tone="neutral">{suggestion.source_status}</Badge>
                        ) : null}
                      </div>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      <button
                        className="inline-flex h-9 items-center justify-center gap-2 rounded-md border border-mint/40 bg-mint/10 px-3 text-sm text-mint transition hover:bg-mint/15 disabled:opacity-50"
                        disabled={acceptMutation.isPending || ignoreMutation.isPending}
                        onClick={() => acceptMutation.mutate(suggestion.id)}
                        type="button"
                      >
                        <Plus className="h-4 w-4" aria-hidden="true" />
                        <span>Add to Top 3</span>
                      </button>
                      <button
                        className="inline-flex h-9 items-center justify-center gap-2 rounded-md border border-line px-3 text-sm text-muted transition hover:border-red-400 hover:text-red-200 disabled:opacity-50"
                        disabled={acceptMutation.isPending || ignoreMutation.isPending}
                        onClick={() => ignoreMutation.mutate(suggestion.id)}
                        type="button"
                      >
                        <XCircle className="h-4 w-4" aria-hidden="true" />
                        <span>Ignore</span>
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </DashboardCard>
  );
}
