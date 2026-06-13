export function ProbabilityBar({
  value,
  label,
  delta,
  color = "var(--accent)",
}: {
  value: number; // 0..1
  label?: string;
  delta?: number; // 0..1 change vs baseline
  color?: string;
}) {
  const pct = Math.round(value * 100);
  return (
    <div className="w-full">
      {label && (
        <div className="mb-1 flex items-center justify-between text-xs text-muted">
          <span>{label}</span>
          <span className="font-mono text-foreground">
            {pct}%
            {delta !== undefined && Math.abs(delta) >= 0.005 && (
              <span className={delta > 0 ? "text-accent" : "text-danger"}>
                {" "}
                {delta > 0 ? "▲" : "▼"}
                {Math.abs(Math.round(delta * 100))}
              </span>
            )}
          </span>
        </div>
      )}
      <div className="h-2 w-full overflow-hidden rounded-full bg-surface-2">
        <div
          className="h-full rounded-full transition-all"
          style={{ width: `${pct}%`, background: color }}
        />
      </div>
    </div>
  );
}
