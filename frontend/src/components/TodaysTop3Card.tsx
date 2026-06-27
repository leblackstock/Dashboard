import { useMutation, useQueryClient } from "@tanstack/react-query";
import { CheckCircle2, Plus } from "lucide-react";
import { FormEvent, useState } from "react";
import { createTopItem, updateTopItem } from "../lib/api";
import type { Project, TopItem } from "../lib/types";
import { Badge } from "./ui/badge";
import { DashboardCard } from "./DashboardCard";

const inputClass =
  "w-full rounded-md border border-line bg-surface px-3 py-2 text-sm text-ink outline-none transition placeholder:text-muted focus:border-cobalt";

export function TodaysTop3Card({
  items,
  projects
}: {
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
      </div>
    </DashboardCard>
  );
}
