import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus } from "lucide-react";
import { FormEvent, useState } from "react";
import { createQuickCapture } from "../lib/api";
import type { Project, QuickCapture } from "../lib/types";
import { DashboardCard } from "./DashboardCard";
import { Badge } from "./ui/badge";

const inputClass =
  "w-full rounded-md border border-line bg-surface px-3 py-2 text-sm text-ink outline-none transition placeholder:text-muted focus:border-cobalt";

function formatTime(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "—";
  return new Intl.DateTimeFormat(undefined, {
    hour: "numeric",
    minute: "2-digit"
  }).format(date);
}

export function QuickCaptureCard({
  captures,
  projects
}: {
  captures: QuickCapture[];
  projects: Project[];
}) {
  const queryClient = useQueryClient();
  const [text, setText] = useState("");
  const [projectKey, setProjectKey] = useState("");
  const [captureType, setCaptureType] = useState("note");

  const createMutation = useMutation({
    mutationFn: createQuickCapture,
    onSuccess: () => {
      setText("");
      setProjectKey("");
      setCaptureType("note");
      void queryClient.invalidateQueries({ queryKey: ["daily-dashboard"] });
    }
  });

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = text.trim();
    if (!trimmed) return;
    createMutation.mutate({
      text: trimmed,
      project_key: projectKey || null,
      capture_type: captureType,
      status: "new"
    });
  }

  return (
    <DashboardCard title="Quick Capture" eyebrow="Inbox">
      <div className="space-y-4">
        <form className="space-y-2" onSubmit={handleSubmit}>
          <textarea
            className={`${inputClass} min-h-[104px] resize-y`}
            value={text}
            onChange={(event) => setText(event.target.value)}
            placeholder="Capture a note"
            maxLength={2000}
          />
          <div className="grid gap-2 sm:grid-cols-[1fr_140px_40px]">
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
              value={captureType}
              onChange={(event) => setCaptureType(event.target.value)}
              aria-label="Type"
            >
              <option value="note">Note</option>
              <option value="task">Task</option>
              <option value="idea">Idea</option>
              <option value="blocker">Blocker</option>
            </select>
            <button
              className="inline-flex h-10 w-10 items-center justify-center rounded-md border border-cobalt/50 bg-cobalt/15 text-ink transition hover:bg-cobalt/25 disabled:opacity-50"
              disabled={createMutation.isPending}
              type="submit"
              title="Save"
              aria-label="Save"
            >
              <Plus className="h-4 w-4" aria-hidden="true" />
            </button>
          </div>
        </form>

        {createMutation.isError ? (
          <p className="text-sm text-red-200">Capture was rejected.</p>
        ) : null}

        <div className="space-y-2">
          {captures.length === 0 ? (
            <p className="text-sm text-muted">No captures waiting.</p>
          ) : (
            captures.map((capture) => (
              <div
                key={capture.id}
                className="rounded-md border border-line bg-surface p-3"
              >
                <p className="break-words text-sm text-ink">{capture.text}</p>
                <div className="mt-2 flex flex-wrap gap-2">
                  <Badge tone="neutral">{capture.capture_type ?? "note"}</Badge>
                  <Badge tone="neutral">{formatTime(capture.captured_at)}</Badge>
                  {capture.project_label ? (
                    <Badge tone="neutral">{capture.project_label}</Badge>
                  ) : null}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </DashboardCard>
  );
}
