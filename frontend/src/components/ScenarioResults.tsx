import type { SimulateResponse, TeamProbabilities } from "@/lib/types";
import { Card } from "./Card";
import { KnockoutPathView } from "./KnockoutPathView";
import { ProbabilityBar } from "./ProbabilityBar";
import { ProbabilityFunnel } from "./ProbabilityFunnel";
import { ShareButton } from "./ShareButton";
import { StandingsTable } from "./StandingsTable";
import { TeamBadge } from "./TeamBadge";

export function ScenarioResults({
  result,
  baseline,
}: {
  result: SimulateResponse;
  baseline: Map<number, TeamProbabilities>;
}) {
  const focusId = result.knockout_path?.team_id;
  const probByTeam = new Map(result.qualification_probabilities.map((p) => [p.team_id, p]));
  const focusProb = focusId ? probByTeam.get(focusId) : undefined;
  const focusBase = focusId ? baseline.get(focusId) : undefined;
  const focusGroup = focusProb
    ? result.updated_standings.find((g) => g.group_name === focusProb.group_name)
    : undefined;

  // Biggest qualification swings vs baseline (excluding the focus team).
  const movers = result.qualification_probabilities
    .map((p) => {
      const b = baseline.get(p.team_id);
      return {
        p,
        delta: b ? p.qualification_probability - b.qualification_probability : 0,
      };
    })
    .filter((m) => Math.abs(m.delta) >= 0.01 && m.p.team_id !== focusId)
    .sort((a, b) => Math.abs(b.delta) - Math.abs(a.delta))
    .slice(0, 5);

  const nextOpp = result.knockout_path?.rounds[0]?.opponent;

  return (
    <div className="space-y-4">
      {result.parsed_query && (
        <div className="rounded-lg border border-accent/30 bg-accent/5 px-4 py-2 text-sm">
          Interpreted as: <span className="font-medium">{result.parsed_query}</span>
        </div>
      )}

      {result.ai_summary && (
        <Card title="Analysis">
          <p className="leading-relaxed">{result.ai_summary}</p>
          {focusProb && focusBase && (
            <div className="mt-4">
              <ShareButton
                scenarioText={result.parsed_query ?? "Scenario"}
                team={focusProb.team}
                before={focusBase.qualification_probability}
                after={focusProb.qualification_probability}
                opponent={nextOpp}
              />
            </div>
          )}
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-2">
        {focusProb && (
          <Card title="Probability outlook">
            <div className="mb-3 flex items-center gap-2 font-semibold">
              <TeamBadge code={focusProb.fifa_code} name={focusProb.team} teamId={focusProb.team_id} />
            </div>
            <ProbabilityFunnel probs={focusProb} baseline={focusBase} />
          </Card>
        )}

        {result.knockout_path && (
          <Card title="Knockout path">
            <KnockoutPathView path={result.knockout_path} />
          </Card>
        )}
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {focusGroup && (
          <Card title={`Updated standings · Group ${focusGroup.group_name}`}>
            <StandingsTable table={focusGroup} />
          </Card>
        )}

        {movers.length > 0 && (
          <Card title="Biggest ripple effects">
            <div className="space-y-3">
              {movers.map((m) => (
                <div key={m.p.team_id} className="flex items-center gap-3">
                  <div className="w-28 shrink-0">
                    <TeamBadge code={m.p.fifa_code} name={m.p.team} teamId={m.p.team_id} size="sm" />
                  </div>
                  <div className="flex-1">
                    <ProbabilityBar
                      value={m.p.qualification_probability}
                      delta={m.delta}
                      color={m.delta > 0 ? "var(--accent)" : "var(--danger)"}
                    />
                  </div>
                </div>
              ))}
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}
