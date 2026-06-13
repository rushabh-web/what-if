import type { KnockoutPath } from "@/lib/types";
import { TeamBadge } from "./TeamBadge";

export function KnockoutPathView({ path }: { path: KnockoutPath }) {
  if (!path.rounds.length) {
    return (
      <p className="text-sm text-muted">
        {path.team} is not projected to reach the knockout stage in this scenario.
      </p>
    );
  }
  return (
    <div className="space-y-2">
      <p className="text-xs text-muted">
        Projected route · seeded{" "}
        <span className="font-mono text-foreground">{path.seeded_position}</span>
      </p>
      <ol className="relative space-y-3 border-l border-border pl-5">
        {path.rounds.map((r, i) => (
          <li key={i} className="relative">
            <span className="absolute -left-[1.42rem] top-1.5 h-2.5 w-2.5 rounded-full bg-accent" />
            <div className="flex items-center justify-between gap-2">
              <div>
                <div className="text-xs text-muted">{r.round_name}</div>
                <TeamBadge code={r.opponent_code} name={r.opponent} teamId={r.opponent_team_id ?? undefined} size="sm" />
              </div>
              <div className="text-right">
                <div className="font-mono text-sm">
                  {Math.round(r.win_probability * 100)}%
                </div>
                <div className="text-[10px] text-muted">win tie</div>
              </div>
            </div>
          </li>
        ))}
      </ol>
    </div>
  );
}
