import type { ReactNode } from "react";

type BadgeTone = "neutral" | "fresh" | "warn" | "stale";

const toneClasses: Record<BadgeTone, string> = {
  neutral: "border-line/70 bg-surface/70 text-muted",
  fresh: "border-mint/40 bg-mint/10 text-mint",
  warn: "border-amber/40 bg-amber/10 text-amber",
  stale: "border-danger/40 bg-danger/10 text-danger"
};

export function Badge({
  children,
  tone = "neutral"
}: {
  children: ReactNode;
  tone?: BadgeTone;
}) {
  return (
    <span
      className={`inline-flex h-7 items-center rounded-md border px-2.5 text-xs font-medium shadow-[inset_0_1px_0_rgb(255_255_255_/_0.04)] backdrop-blur-sm ${toneClasses[tone]}`}
    >
      {children}
    </span>
  );
}
