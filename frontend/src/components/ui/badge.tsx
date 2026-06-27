import type { ReactNode } from "react";

type BadgeTone = "neutral" | "fresh" | "warn" | "stale";

const toneClasses: Record<BadgeTone, string> = {
  neutral: "border-line bg-surface text-muted",
  fresh: "border-mint/40 bg-mint/10 text-mint",
  warn: "border-amber/40 bg-amber/10 text-amber",
  stale: "border-red-400/40 bg-red-400/10 text-red-200"
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
      className={`inline-flex h-7 items-center rounded-md border px-2.5 text-xs font-medium ${toneClasses[tone]}`}
    >
      {children}
    </span>
  );
}
