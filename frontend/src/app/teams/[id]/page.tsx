"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import type { TeamOutlook } from "@/lib/types";
import { Card } from "@/components/Card";
import { KnockoutPathView } from "@/components/KnockoutPathView";
import { ProbabilityFunnel } from "@/components/ProbabilityFunnel";
import { TeamBadge } from "@/components/TeamBadge";

export default function TeamExplorerPage() {
  const params = useParams<{ id: string }>();
  const id = Number(params.id);
  const [data, setData] = useState<TeamOutlook | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    api
      .teamOutlook(id)
      .then(setData)
      .catch((e) => setError(String(e)));
  }, [id]);

  if (error)
    return (
      <div className="rounded-lg border border-danger/40 bg-danger/10 px-4 py-2 text-sm text-danger">
        {error}
      </div>
    );
  if (!data) return <p className="text-sm text-muted">Loading team…</p>;

  const fmtDate = (d: string) =>
    new Date(d).toLocaleDateString(undefined, { month: "short", day: "numeric" });

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <TeamBadge code={data.team.fifa_code} />
          <div>
            <h1 className="text-2xl font-bold">{data.team.name}</h1>
            <p className="text-sm text-muted">Group {data.team.group_name}</p>
          </div>
        </div>
        <Link href="/groups" className="text-sm text-muted hover:text-accent">
          ← All groups
        </Link>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card title="Qualification & deep-run odds">
          {data.probabilities ? (
            <ProbabilityFunnel probs={data.probabilities} />
          ) : (
            <p className="text-sm text-muted">No probabilities available.</p>
          )}
        </Card>

        <Card title="Projected knockout path">
          {data.knockout_path ? (
            <KnockoutPathView path={data.knockout_path} />
          ) : (
            <p className="text-sm text-muted">Not projected to qualify.</p>
          )}
        </Card>
      </div>

      <Card title="Remaining matches">
        {data.remaining_matches.length === 0 ? (
          <p className="text-sm text-muted">No matches remaining.</p>
        ) : (
          <ul className="divide-y divide-border/60">
            {data.remaining_matches.map((m) => (
              <li key={m.match_id} className="flex items-center justify-between py-2.5 text-sm">
                <div className="flex items-center gap-2">
                  <TeamBadge code={m.home_code} teamId={m.home_team_id} size="sm" />
                  <span className="text-muted">vs</span>
                  <TeamBadge code={m.away_code} teamId={m.away_team_id} size="sm" />
                </div>
                <span className="text-xs text-muted">
                  MD{m.matchday} · {fmtDate(m.match_date)}
                </span>
              </li>
            ))}
          </ul>
        )}
      </Card>
    </div>
  );
}
