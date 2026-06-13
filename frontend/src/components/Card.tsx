export function Card({
  title,
  children,
  className = "",
}: {
  title?: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <section
      className={`rounded-2xl border border-border bg-surface p-5 ${className}`}
    >
      {title && <h2 className="mb-4 text-sm font-semibold text-muted">{title}</h2>}
      {children}
    </section>
  );
}
