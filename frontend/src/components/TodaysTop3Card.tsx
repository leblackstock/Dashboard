import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  ArrowUpCircle,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  CircleMinus,
  GripVertical,
  Plus,
  RefreshCcw,
  RotateCcw,
  XCircle
} from "lucide-react";
import {
  FormEvent,
  KeyboardEvent,
  PointerEvent as ReactPointerEvent,
  useEffect,
  useRef,
  useState
} from "react";
import {
  acceptBriefSuggestion,
  createTopItem,
  DashboardApiError,
  ignoreBriefSuggestion,
  importBriefSuggestions,
  promoteTopItem,
  removeTopItem,
  reorderTopItems,
  returnTopItemToSuggestions,
  updateTopItem
} from "../lib/api";
import type { BriefSuggestion, Project, TopItem } from "../lib/types";
import { DashboardCard } from "./DashboardCard";
import { Badge } from "./ui/badge";

const PRIORITY_QUEUE_STORAGE_KEY = "dashboard.priority-queue.expanded.v1";
const inputClass =
  "w-full rounded-md border border-line bg-surface px-3 py-2 text-sm text-ink outline-none transition placeholder:text-muted focus:border-cobalt";

function sortPriorities(items: TopItem[]) {
  return [...items].sort(
    (left, right) =>
      left.sort_order - right.sort_order ||
      left.created_at.localeCompare(right.created_at) ||
      left.id - right.id
  );
}

function loadQueueExpanded() {
  if (typeof window === "undefined") return false;
  try {
    return window.localStorage.getItem(PRIORITY_QUEUE_STORAGE_KEY) === "true";
  } catch {
    return false;
  }
}

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
  const [actionMessage, setActionMessage] = useState("");
  const [queueExpanded, setQueueExpanded] = useState(loadQueueExpanded);
  const [activeItems, setActiveItems] = useState(() =>
    sortPriorities(items.filter((item) => item.status === "active"))
  );
  const [draggingId, setDraggingId] = useState<number | null>(null);
  const [dropTargetId, setDropTargetId] = useState<number | null>(null);
  const pointerDrag = useRef<{
    sourceId: number;
    startX: number;
    startY: number;
    targetId: number | null;
    active: boolean;
  } | null>(null);

  const queuedItems = sortPriorities(items.filter((item) => item.status === "queued"));
  const completedToday = items.filter(
    (item) => item.display_state === "completed_today"
  );
  const activeFull = activeItems.length >= 3;

  useEffect(() => {
    setActiveItems(sortPriorities(items.filter((item) => item.status === "active")));
  }, [items]);

  function refreshDaily() {
    return queryClient.invalidateQueries({ queryKey: ["daily-dashboard"] });
  }

  const createMutation = useMutation({
    mutationFn: createTopItem,
    onSuccess: (result) => {
      setTitle("");
      setProjectKey("");
      setActionMessage(result.message);
      void refreshDaily();
    }
  });

  const completeMutation = useMutation({
    mutationFn: (id: number) => updateTopItem(id, { status: "completed" }),
    onSuccess: () => {
      setActionMessage("Priority completed.");
      void refreshDaily();
    }
  });

  const promoteMutation = useMutation({
    mutationFn: promoteTopItem,
    onSuccess: (result) => {
      setActionMessage(result.message);
      void refreshDaily();
    },
    onError: (error) => {
      setActionMessage(
        error instanceof DashboardApiError && error.safeCode === "top_3_full"
          ? "Top 3 is full. Remove or complete one first."
          : "Unable to promote priority."
      );
      void refreshDaily();
    }
  });

  const removeMutation = useMutation({
    mutationFn: removeTopItem,
    onSuccess: () => {
      setActionMessage("Removed from today.");
      void refreshDaily();
    }
  });

  const returnMutation = useMutation({
    mutationFn: returnTopItemToSuggestions,
    onSuccess: () => {
      setActionMessage("Returned to Brief suggestions.");
      void refreshDaily();
    }
  });

  const reorderMutation = useMutation({
    mutationFn: reorderTopItems,
    onSuccess: () => void refreshDaily(),
    onError: () => {
      setActionMessage("Unable to save priority order.");
      void refreshDaily();
    }
  });

  const importMutation = useMutation({
    mutationFn: importBriefSuggestions,
    onSuccess: () => void refreshDaily()
  });

  const acceptMutation = useMutation({
    mutationFn: acceptBriefSuggestion,
    onSuccess: (result) => {
      setActionMessage(result.message);
      void refreshDaily();
    }
  });

  const ignoreMutation = useMutation({
    mutationFn: ignoreBriefSuggestion,
    onSuccess: () => void refreshDaily()
  });

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = title.trim();
    if (!trimmed) return;
    setActionMessage("");
    createMutation.mutate({
      title: trimmed,
      project_key: projectKey || null
    });
  }

  function toggleQueue() {
    const nextValue = !queueExpanded;
    setQueueExpanded(nextValue);
    try {
      window.localStorage.setItem(PRIORITY_QUEUE_STORAGE_KEY, String(nextValue));
    } catch {
      // The queue still works when browser storage is unavailable.
    }
  }

  function saveActiveOrder(nextItems: TopItem[]) {
    setActiveItems(nextItems);
    reorderMutation.mutate(nextItems.map((item) => item.id));
  }

  function moveActiveItem(sourceId: number, targetId: number) {
    if (sourceId === targetId) return;
    const nextItems = [...activeItems];
    const sourceIndex = nextItems.findIndex((item) => item.id === sourceId);
    const targetIndex = nextItems.findIndex((item) => item.id === targetId);
    if (sourceIndex < 0 || targetIndex < 0) return;
    const [moved] = nextItems.splice(sourceIndex, 1);
    nextItems.splice(targetIndex, 0, moved);
    saveActiveOrder(nextItems);
  }

  function moveActiveItemByOffset(itemId: number, offset: number) {
    const sourceIndex = activeItems.findIndex((item) => item.id === itemId);
    const targetIndex = sourceIndex + offset;
    if (sourceIndex < 0 || targetIndex < 0 || targetIndex >= activeItems.length) return;
    moveActiveItem(itemId, activeItems[targetIndex].id);
  }

  function handleDragPointerDown(
    event: ReactPointerEvent<HTMLButtonElement>,
    itemId: number
  ) {
    if (event.button !== 0) return;
    pointerDrag.current = {
      sourceId: itemId,
      startX: event.clientX,
      startY: event.clientY,
      targetId: null,
      active: false
    };
    event.currentTarget.setPointerCapture(event.pointerId);
  }

  function handleDragPointerMove(event: ReactPointerEvent<HTMLButtonElement>) {
    const drag = pointerDrag.current;
    if (!drag) return;
    if (!drag.active) {
      const distance = Math.hypot(
        event.clientX - drag.startX,
        event.clientY - drag.startY
      );
      if (distance < 5) return;
      drag.active = true;
      setDraggingId(drag.sourceId);
    }
    event.preventDefault();
    const target = document
      .elementFromPoint(event.clientX, event.clientY)
      ?.closest<HTMLElement>("[data-active-priority-id]");
    const targetId = target ? Number(target.dataset.activePriorityId) : null;
    drag.targetId = Number.isFinite(targetId) ? targetId : null;
    setDropTargetId(drag.targetId);
  }

  function handleDragPointerEnd(event: ReactPointerEvent<HTMLButtonElement>) {
    const drag = pointerDrag.current;
    if (drag?.active && drag.targetId) {
      moveActiveItem(drag.sourceId, drag.targetId);
    }
    if (event.currentTarget.hasPointerCapture(event.pointerId)) {
      event.currentTarget.releasePointerCapture(event.pointerId);
    }
    pointerDrag.current = null;
    setDraggingId(null);
    setDropTargetId(null);
  }

  function handleDragKeyDown(event: KeyboardEvent<HTMLButtonElement>, itemId: number) {
    if (event.key === "ArrowUp") {
      event.preventDefault();
      moveActiveItemByOffset(itemId, -1);
    } else if (event.key === "ArrowDown") {
      event.preventDefault();
      moveActiveItemByOffset(itemId, 1);
    }
  }

  const importFailed = importMutation.isError || importMutation.data?.status === "failed";
  const importSummary = importMutation.data
    ? importMutation.data.status === "success"
      ? `${importMutation.data.message} Imported ${importMutation.data.imported}, already imported ${importMutation.data.already_imported}, skipped ${importMutation.data.skipped}, duplicates hidden ${importMutation.data.duplicates_hidden}.`
      : importMutation.data.message
    : null;
  const mutationBusy =
    completeMutation.isPending ||
    promoteMutation.isPending ||
    removeMutation.isPending ||
    returnMutation.isPending ||
    reorderMutation.isPending;

  return (
    <DashboardCard title="Today’s Top 3" eyebrow="Focus">
      <div className="space-y-4" data-testid="todays-top3-card">
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
        {actionMessage ? (
          <p
            className="rounded-md border border-cobalt/30 bg-cobalt/10 px-3 py-2 text-sm text-ink"
            aria-live="polite"
          >
            {actionMessage}
          </p>
        ) : null}

        <section aria-labelledby="active-top-three-heading" data-testid="active-top-three">
          <div className="mb-2 flex items-center justify-between gap-3">
            <p id="active-top-three-heading" className="text-sm font-medium text-ink">
              Active Top 3
            </p>
            <span className="text-xs text-muted">{activeItems.length} of 3</span>
          </div>
          <div className="space-y-2">
            {activeItems.length === 0 ? (
              <p className="text-sm text-muted">No active priorities.</p>
            ) : (
              activeItems.map((item) => (
                <PriorityItemRow
                  activeFull={activeFull}
                  busy={mutationBusy}
                  canDrag
                  dragging={draggingId === item.id}
                  dropTarget={dropTargetId === item.id}
                  item={item}
                  key={item.id}
                  onComplete={() => completeMutation.mutate(item.id)}
                  onDragKeyDown={(event) => handleDragKeyDown(event, item.id)}
                  onDragPointerDown={(event) => handleDragPointerDown(event, item.id)}
                  onDragPointerEnd={handleDragPointerEnd}
                  onDragPointerMove={handleDragPointerMove}
                  onPromote={() => undefined}
                  onRemove={() => removeMutation.mutate(item.id)}
                  onReturn={() => returnMutation.mutate(item.id)}
                />
              ))
            )}
          </div>
        </section>

        {completedToday.length > 0 ? (
          <section className="space-y-2" aria-label="Completed today">
            {completedToday.map((item) => (
              <div
                className="rounded-md border border-line bg-surface p-3 opacity-55"
                key={item.id}
              >
                <p className="break-words text-sm font-medium text-ink line-through">
                  {item.title}
                </p>
                <div className="mt-2 flex flex-wrap gap-2">
                  {item.project_label ? (
                    <Badge tone="neutral">{item.project_label}</Badge>
                  ) : null}
                  <Badge tone="fresh">done today</Badge>
                </div>
              </div>
            ))}
          </section>
        ) : null}

        <section className="border-t border-line pt-3" data-testid="priority-queue">
          <button
            className="flex w-full items-center justify-between gap-3 rounded-md px-1 py-2 text-left text-sm font-medium text-ink transition hover:text-cobalt"
            onClick={toggleQueue}
            type="button"
            aria-expanded={queueExpanded}
          >
            <span>Priority Queue · {queuedItems.length} waiting</span>
            {queueExpanded ? (
              <ChevronUp className="h-4 w-4" aria-hidden="true" />
            ) : (
              <ChevronDown className="h-4 w-4" aria-hidden="true" />
            )}
          </button>
          {queueExpanded ? (
            <div className="mt-2 space-y-2">
              {activeFull && queuedItems.length > 0 ? (
                <p className="text-xs text-muted">
                  Top 3 is full. Remove or complete one first.
                </p>
              ) : null}
              {queuedItems.length === 0 ? (
                <p className="text-sm text-muted">No queued priorities.</p>
              ) : (
                queuedItems.map((item) => (
                  <PriorityItemRow
                    activeFull={activeFull}
                    busy={mutationBusy}
                    canDrag={false}
                    dragging={false}
                    dropTarget={false}
                    item={item}
                    key={item.id}
                    onComplete={() => completeMutation.mutate(item.id)}
                    onDragKeyDown={() => undefined}
                    onDragPointerDown={() => undefined}
                    onDragPointerEnd={() => undefined}
                    onDragPointerMove={() => undefined}
                    onPromote={() => promoteMutation.mutate(item.id)}
                    onRemove={() => removeMutation.mutate(item.id)}
                    onReturn={() => returnMutation.mutate(item.id)}
                  />
                ))
              )}
            </div>
          ) : null}
        </section>

        <div
          className="border-t border-line pt-4"
          data-testid="brief-suggestions"
        >
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
                  data-brief-suggestion-id={suggestion.id}
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

function PriorityItemRow({
  activeFull,
  busy,
  canDrag,
  dragging,
  dropTarget,
  item,
  onComplete,
  onDragKeyDown,
  onDragPointerDown,
  onDragPointerEnd,
  onDragPointerMove,
  onPromote,
  onRemove,
  onReturn
}: {
  activeFull: boolean;
  busy: boolean;
  canDrag: boolean;
  dragging: boolean;
  dropTarget: boolean;
  item: TopItem;
  onComplete: () => void;
  onDragKeyDown: (event: KeyboardEvent<HTMLButtonElement>) => void;
  onDragPointerDown: (event: ReactPointerEvent<HTMLButtonElement>) => void;
  onDragPointerEnd: (event: ReactPointerEvent<HTMLButtonElement>) => void;
  onDragPointerMove: (event: ReactPointerEvent<HTMLButtonElement>) => void;
  onPromote: () => void;
  onRemove: () => void;
  onReturn: () => void;
}) {
  return (
    <div
      className={`rounded-md border bg-surface p-3 transition ${
        dropTarget ? "border-cobalt ring-1 ring-cobalt/50" : "border-line"
      } ${dragging ? "opacity-55" : ""}`}
      data-active-priority-id={canDrag ? item.id : undefined}
      data-priority-item-id={item.id}
      data-priority-status={item.status}
    >
      <div className="flex items-start gap-2">
        {canDrag ? (
          <button
            className="inline-flex h-8 w-8 shrink-0 touch-none cursor-grab items-center justify-center rounded-md text-muted transition hover:bg-panel hover:text-ink active:cursor-grabbing"
            onKeyDown={onDragKeyDown}
            onPointerCancel={onDragPointerEnd}
            onPointerDown={onDragPointerDown}
            onPointerMove={onDragPointerMove}
            onPointerUp={onDragPointerEnd}
            type="button"
            title="Drag to reorder"
            aria-label={`Reorder ${item.title}`}
          >
            <GripVertical className="h-4 w-4" aria-hidden="true" />
          </button>
        ) : null}
        <div className="min-w-0 flex-1">
          <p className="break-words text-sm font-medium text-ink">{item.title}</p>
          <div className="mt-2 flex flex-wrap gap-2">
            {item.project_label ? (
              <Badge tone="neutral">{item.project_label}</Badge>
            ) : null}
            {item.source_label ? <Badge tone="neutral">{item.source_label}</Badge> : null}
          </div>
        </div>
        <div className="flex shrink-0 flex-wrap justify-end gap-1">
          {!canDrag ? (
            <button
              className="inline-flex h-8 items-center justify-center gap-1.5 rounded-md border border-cobalt/40 px-2 text-xs text-cobalt transition hover:bg-cobalt/10 disabled:cursor-not-allowed disabled:opacity-40"
              disabled={busy || activeFull}
              onClick={onPromote}
              type="button"
              title={
                activeFull
                  ? "Top 3 is full. Remove or complete one first."
                  : "Promote to Top 3"
              }
            >
              <ArrowUpCircle className="h-4 w-4" aria-hidden="true" />
              <span>Promote</span>
            </button>
          ) : null}
          <button
            className="inline-flex h-8 w-8 items-center justify-center rounded-md border border-line text-muted transition hover:border-mint hover:text-mint disabled:opacity-40"
            disabled={busy}
            onClick={onComplete}
            type="button"
            title="Complete"
            aria-label="Complete"
          >
            <CheckCircle2 className="h-4 w-4" aria-hidden="true" />
          </button>
          <button
            className="inline-flex h-8 w-8 items-center justify-center rounded-md border border-line text-muted transition hover:border-amber hover:text-amber disabled:opacity-40"
            disabled={busy}
            onClick={onRemove}
            type="button"
            title="Remove from Today"
            aria-label="Remove from Today"
          >
            <CircleMinus className="h-4 w-4" aria-hidden="true" />
          </button>
          {item.source_suggestion_key ? (
            <button
              className="inline-flex h-8 w-8 items-center justify-center rounded-md border border-line text-muted transition hover:border-cobalt hover:text-cobalt disabled:opacity-40"
              disabled={busy}
              onClick={onReturn}
              type="button"
              title="Return to Suggestions"
              aria-label="Return to Suggestions"
            >
              <RotateCcw className="h-4 w-4" aria-hidden="true" />
            </button>
          ) : null}
        </div>
      </div>
    </div>
  );
}
