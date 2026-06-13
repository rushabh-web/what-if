import Link from "next/link";

// Deterministic accent color from the FIFA code (stand-in for flags).
function codeColor(code: string): string {
  let h = 0;
  for (let i = 0; i < code.length; i++) h = (h * 31 + code.charCodeAt(i)) % 360;
  return `hsl(${h} 55% 42%)`;
}

export function TeamBadge({
  code,
  name,
  teamId,
  size = "md",
}: {
  code: string;
  name?: string;
  teamId?: number;
  size?: "sm" | "md";
}) {
  const dim = size === "sm" ? "h-6 w-9 text-[10px]" : "h-7 w-10 text-xs";
  const badge = (
    <span className="inline-flex items-center gap-2">
      <span
        className={`inline-flex ${dim} items-center justify-center rounded font-bold tracking-wide text-white shadow-sm`}
        style={{ background: codeColor(code) }}
      >
        {code}
      </span>
      {name && <span className="truncate">{name}</span>}
    </span>
  );
  if (teamId) {
    return (
      <Link href={`/teams/${teamId}`} className="hover:text-accent">
        {badge}
      </Link>
    );
  }
  return badge;
}
