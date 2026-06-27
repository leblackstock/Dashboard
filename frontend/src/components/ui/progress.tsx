export function Progress({ value }: { value: number | null }) {
  const normalized = value == null ? 0 : Math.max(0, Math.min(100, value));
  return (
    <div className="h-2 w-full overflow-hidden rounded-md bg-surface">
      <div className="h-full rounded-md bg-cobalt" style={{ width: `${normalized}%` }} />
    </div>
  );
}
