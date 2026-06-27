import { useMutation, useQueryClient } from "@tanstack/react-query";
import { CheckCircle2, Plus } from "lucide-react";
import { FormEvent, useState } from "react";
import { createBlockedItem, updateBlockedItem } from "../lib/api";
import type { BlockedItem, BlockedItemStatus, Project } from "../lib/types";
import { DashboardCard } from "./DashboardCard";
import { Badge } from "./ui/badge";

const inputClass =
  "w-full rounded-md border border-line bg-surface px-3 py-2 text-sm text-ink outline-none transition placeholder:text-muted focus:border-cobalt";

function badgeTone(status: BlockedItemStatus) {
  if (status === "Blocked") return "stale";
  if (status === "Needs Review") return "warn";
  return "fresh";
}

export function BlockedReviewCard({
  items,
  projects
}: {
  items: BlockedItem[];
  projects: Project[];
}) {
  const queryClient = useQueryClient();
  const [title, setTitle] = useState("");
  const [projectKey, setProjectKey] = useState("");
  const [status, setStatus] = useState<BlockedItemStatus>("Blocked");

  const createMutation = useMutation({
    mutationFn: createBlockedItem,
    onSuccess: () => {
      setTitle("");
      setProjectKey("");
      setStatus("Blocked");
      void queryClient.invalidateQueries({ queryKey: ["daily-dashboard"] });
    }
  });

  const resolveMutation = useMutation({
    mutationFn: (id: number) => updateBlockedItem(id, { status: "Resolved" }),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["daily-dashboard"] })
  });

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = title.trim();
    if (!trimmed) return;
    createMutation.mutate({
      title: trimmed,
      project_key: projectKey || null,
      status
    });
  }

  return (
    <DashboardCard title="Blocked / Needs Review" eyebrow="Attention">
      <div className="space-y-4">
        <form className="grid gap-2 sm:grid-cols-[1fr_150px_150px_40px]" onSubmit={handleSubmit}>
          <input
            className={inputClass}
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            placeholder="Add item"
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
          <select
            className={inputClass}
            value={status}
            onChange={(event) => setStatus(event.target.value as BlockedItemStatus)}
            aria-label="Status"
          >
            <option value="Blocked">Blocked</option>
            <option value="Needs Review">Needs Review</option>
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
          <p className="text-sm text-red-200">Unable to add item.</p>
        ) : null}

        <div className="space-y-2">
          {items.length === 0 ? (
            <p className="text-sm text-muted">Nothing blocked.</p>
          ) : (
            items.map((item) => (
              <div
                key={item.id}
                className="rounded-md border border-line bg-surface p-3"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <p className="break-words text-sm font-medium text-ink">{item.title}</p>
                    <div className="mt-2 flex flex-wrap gap-2">
                      <Badge tone={badgeTone(item.status)}>{item.status}</Badge>
                      {item.project_label ? (
                        <Badge tone="neutral">{item.project_label}</Badge>
                      ) : null}
                    </div>
                  </div>
                  <button
                    className="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-md border border-line text-muted transition hover:border-mint hover:text-mint disabled:opacity-50"
                    disabled={resolveMutation.isPending}
                    onClick={() => resolveMutation.mutate(item.id)}
                    type="button"
                    title="Resolve"
                    aria-label="Resolve"
                  >
                    <CheckCircle2 className="h-4 w-4" aria-hidden="true" />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </DashboardCard>
  );
}
