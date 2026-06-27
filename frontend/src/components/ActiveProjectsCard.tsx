import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus } from "lucide-react";
import { FormEvent, useState } from "react";
import { createProject } from "../lib/api";
import type { Project } from "../lib/types";
import { DashboardCard } from "./DashboardCard";
import { Badge } from "./ui/badge";

const inputClass =
  "w-full rounded-md border border-line bg-surface px-3 py-2 text-sm text-ink outline-none transition placeholder:text-muted focus:border-cobalt";

export function ActiveProjectsCard({ projects }: { projects: Project[] }) {
  const queryClient = useQueryClient();
  const [projectLabel, setProjectLabel] = useState("");
  const activeProjects = projects.filter((project) => project.status === "Active");

  const createMutation = useMutation({
    mutationFn: createProject,
    onSuccess: () => {
      setProjectLabel("");
      void queryClient.invalidateQueries({ queryKey: ["daily-dashboard"] });
    }
  });

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = projectLabel.trim();
    if (!trimmed) return;
    createMutation.mutate({ project_label: trimmed, status: "Active" });
  }

  return (
    <DashboardCard title="Active Projects" eyebrow="Registry">
      <div className="space-y-4">
        <form className="grid grid-cols-[1fr_40px] gap-2" onSubmit={handleSubmit}>
          <input
            className={inputClass}
            value={projectLabel}
            onChange={(event) => setProjectLabel(event.target.value)}
            placeholder="Add project"
            maxLength={160}
          />
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
          <p className="text-sm text-red-200">Unable to add project.</p>
        ) : null}

        <div className="space-y-2">
          {activeProjects.length === 0 ? (
            <p className="text-sm text-muted">No active projects.</p>
          ) : (
            activeProjects.slice(0, 8).map((project) => (
              <div
                key={project.project_key}
                className="flex items-center justify-between gap-3 rounded-md border border-line bg-surface p-3"
              >
                <div className="min-w-0">
                  <p className="break-words text-sm font-medium text-ink">
                    {project.project_label}
                  </p>
                  {project.default_ai_tool ? (
                    <p className="mt-1 text-xs text-muted">{project.default_ai_tool}</p>
                  ) : null}
                </div>
                <Badge tone="fresh">{project.status}</Badge>
              </div>
            ))
          )}
        </div>
      </div>
    </DashboardCard>
  );
}
