import type { PointerEvent as ReactPointerEvent, ReactNode } from "react";
import { useRef, useState } from "react";

export const DASHBOARD_LAYOUT_STORAGE_KEY = "dashboard.card-order.v1";

export const DEFAULT_DASHBOARD_CARD_ORDER = [
  "codex-usage",
  "todays-top3",
  "active-projects",
  "blocked-review",
  "quick-capture",
  "collector-health"
] as const;

export type DashboardCardId = (typeof DEFAULT_DASHBOARD_CARD_ORDER)[number];

type DashboardCardDefinition = {
  label: string;
  content: ReactNode;
};

export function loadDashboardCardOrder(): DashboardCardId[] {
  if (typeof window === "undefined") {
    return [...DEFAULT_DASHBOARD_CARD_ORDER];
  }
  try {
    const rawValue = window.localStorage.getItem(DASHBOARD_LAYOUT_STORAGE_KEY);
    if (!rawValue) {
      return [...DEFAULT_DASHBOARD_CARD_ORDER];
    }
    const stored = JSON.parse(rawValue);
    if (!Array.isArray(stored)) {
      window.localStorage.removeItem(DASHBOARD_LAYOUT_STORAGE_KEY);
      return [...DEFAULT_DASHBOARD_CARD_ORDER];
    }
    const validIds = new Set<DashboardCardId>(DEFAULT_DASHBOARD_CARD_ORDER);
    const normalized = stored.filter(
      (value, index): value is DashboardCardId =>
        validIds.has(value as DashboardCardId) && stored.indexOf(value) === index
    );
    for (const cardId of DEFAULT_DASHBOARD_CARD_ORDER) {
      if (!normalized.includes(cardId)) {
        normalized.push(cardId);
      }
    }
    if (JSON.stringify(normalized) !== JSON.stringify(stored)) {
      window.localStorage.setItem(DASHBOARD_LAYOUT_STORAGE_KEY, JSON.stringify(normalized));
    }
    return normalized;
  } catch {
    window.localStorage.removeItem(DASHBOARD_LAYOUT_STORAGE_KEY);
    return [...DEFAULT_DASHBOARD_CARD_ORDER];
  }
}

export function saveDashboardCardOrder(order: DashboardCardId[]) {
  try {
    window.localStorage.setItem(DASHBOARD_LAYOUT_STORAGE_KEY, JSON.stringify(order));
  } catch {
    // The dashboard remains usable when browser storage is unavailable.
  }
}

export function DraggableDashboardGrid({
  cards,
  order,
  onOrderChange
}: {
  cards: Record<DashboardCardId, DashboardCardDefinition>;
  order: DashboardCardId[];
  onOrderChange: (order: DashboardCardId[]) => void;
}) {
  const [draggingId, setDraggingId] = useState<DashboardCardId | null>(null);
  const [dropTargetId, setDropTargetId] = useState<DashboardCardId | null>(null);
  const pointerDrag = useRef<{
    sourceId: DashboardCardId;
    startX: number;
    startY: number;
    active: boolean;
  } | null>(null);
  const currentDropTarget = useRef<DashboardCardId | null>(null);

  function clearDragState() {
    pointerDrag.current = null;
    currentDropTarget.current = null;
    setDraggingId(null);
    setDropTargetId(null);
  }

  function moveCard(sourceId: DashboardCardId, targetId: DashboardCardId) {
    if (sourceId === targetId) return;
    const nextOrder = [...order];
    const sourceIndex = nextOrder.indexOf(sourceId);
    const targetIndex = nextOrder.indexOf(targetId);
    if (sourceIndex < 0 || targetIndex < 0) return;

    const [movedCard] = nextOrder.splice(sourceIndex, 1);
    nextOrder.splice(targetIndex, 0, movedCard);
    onOrderChange(nextOrder);
  }

  function handlePointerDown(event: ReactPointerEvent<HTMLDivElement>) {
    if (event.button !== 0 || !(event.target instanceof Element)) return;
    if (event.target.closest("button, input, select, textarea, a")) return;
    if (!event.target.closest("[data-dashboard-drag-handle]")) return;

    const cardElement = event.target.closest<HTMLElement>("[data-dashboard-card-id]");
    const cardId = cardElement?.dataset.dashboardCardId as DashboardCardId | undefined;
    if (!cardId || !DEFAULT_DASHBOARD_CARD_ORDER.includes(cardId)) return;

    pointerDrag.current = {
      sourceId: cardId,
      startX: event.clientX,
      startY: event.clientY,
      active: false
    };
    event.currentTarget.setPointerCapture(event.pointerId);
  }

  function handlePointerMove(event: ReactPointerEvent<HTMLDivElement>) {
    const drag = pointerDrag.current;
    if (!drag) return;

    if (!drag.active) {
      const distance = Math.hypot(event.clientX - drag.startX, event.clientY - drag.startY);
      if (distance < 6) return;
      drag.active = true;
      setDraggingId(drag.sourceId);
    }

    event.preventDefault();
    const hoveredElement = document.elementFromPoint(event.clientX, event.clientY);
    const hoveredCard = hoveredElement?.closest<HTMLElement>("[data-dashboard-card-id]");
    const hoveredId = hoveredCard?.dataset.dashboardCardId as DashboardCardId | undefined;
    const nextTarget =
      hoveredId && DEFAULT_DASHBOARD_CARD_ORDER.includes(hoveredId) ? hoveredId : null;
    currentDropTarget.current = nextTarget;
    setDropTargetId(nextTarget);
  }

  function handlePointerEnd(event: ReactPointerEvent<HTMLDivElement>) {
    const drag = pointerDrag.current;
    const targetId = currentDropTarget.current;
    if (drag?.active && targetId) {
      moveCard(drag.sourceId, targetId);
    }
    if (event.currentTarget.hasPointerCapture(event.pointerId)) {
      event.currentTarget.releasePointerCapture(event.pointerId);
    }
    clearDragState();
  }

  return (
    <div
      className="columns-1 gap-4 xl:columns-2"
      onPointerCancel={handlePointerEnd}
      onPointerDown={handlePointerDown}
      onPointerMove={handlePointerMove}
      onPointerUp={handlePointerEnd}
    >
      {order.map((cardId) => {
        const card = cards[cardId];
        return (
          <div
            className={`mb-4 inline-block w-full break-inside-avoid align-top transition ${
              draggingId === cardId ? "opacity-55" : ""
            } ${dropTargetId === cardId ? "rounded-lg ring-2 ring-cobalt/60" : ""}`}
            data-dashboard-card-id={cardId}
            key={cardId}
          >
            {card.content}
          </div>
        );
      })}
    </div>
  );
}
