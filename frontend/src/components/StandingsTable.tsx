import type { GroupTable } from "@/lib/types";
import { TeamBadge } from "./TeamBadge";

const STATUS_STYLES: Record<string, string> = {
  qualified: "border-l-2 border-accent",
  third: "border-l-2 border-accent-2/60",
  out: "border-l-2 border-transparent",
};

export function StandingsTable({ table }: { table: GroupTable }) {
  return (
    <div className="overflow-hidden rounded-xl border border-border bg-surface">
      <div className="flex items-center justify-between border-b border-border px-4 py-2.5">
        <h3 className="font-semibold">Group {table.group_name}</h3>
        <span className="text-[10px] uppercase tracking-wider text-muted">
          P W D L GD Pts
        </span>
      </div>
      <table className="w-full text-sm">
        <tbody>
          {table.rows.map((r) => (
            <tr
              key={r.team_id}
              className={`${STATUS_STYLES[r.qualification_status]} border-b border-border/50 last:border-0`}
            >
              <td className="py-2 pl-3 pr-1 text-muted">{r.position}</td>
              <td className="py-2 pr-2">
                <TeamBadge code={r.fifa_code} name={r.team} teamId={r.team_id} size="sm" />
              </td>
              <td className="px-1 text-center text-muted tabular-nums">{r.played}</td>
              <td className="px-1 text-center text-muted tabular-nums">{r.wins}</td>
              <td className="px-1 text-center text-muted tabular-nums">{r.draws}</td>
              <td className="px-1 text-center text-muted tabular-nums">{r.losses}</td>
              <td className="px-1 text-center tabular-nums">
                {r.gd > 0 ? `+${r.gd}` : r.gd}
              </td>
              <td className="px-3 text-center font-semibold tabular-nums">{r.points}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
