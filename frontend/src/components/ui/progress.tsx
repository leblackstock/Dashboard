export function Progress({ value }: { value: number | null }) {
  const normalized = value == null ? 0 : Math.max(0, Math.min(100, value));
  return (
    <div className="h-2 w-full overflow-hidden rounded-md bg-surface/70 shadow-inner shadow-black/30">
      <div
        className="h-full rounded-md bg-gradient-to-r from-cobalt via-violet to-secondary shadow-[0_0_16px_rgb(var(--accent-primary-rgb)_/_0.22)] transition-[width]"
        style={{ width: `${normalized}%` }}
      />
    </div>
  );
}
