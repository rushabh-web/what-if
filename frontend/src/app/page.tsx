"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { SimulateResponse, TeamProbabilities } from "@/lib/types";
import { Card } from "@/components/Card";
import { ProbabilityBar } from "@/components/ProbabilityBar";
import { ScenarioResults } from "@/components/ScenarioResults";
import { TeamBadge } from "@/components/TeamBadge";

const EXAMPLES = [
  "What if Brazil loses today?",
  "Can Morocco still qualify?",
  "What if England wins both matches?",
  "What if Argentina draws?",
];

export default function Home() {
  const [query, setQuery] = useState("");
  const [baseline, setBaseline] = useState<Map<number, TeamProbabilities>>(new Map());
  const [contenders, setContenders] = useState<TeamProbabilities[]>([]);
  const [result, setResult] = useState<SimulateResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [booting, setBooting] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .simulate({})
      .then((res) => {
        setBaseline(new Map(res.qualification_probabilities.map((p) => [p.team_id, p])));
        setContenders(
          [...res.qualification_probabilities]
            .sort((a, b) => b.championship_probability - a.championship_probability)
            .slice(0, 6),
        );
      })
      .catch((e) => setError(String(e)))
      .finally(() => setBooting(false));
  }, []);

  async function run(q: string) {
    if (!q.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.simulate({ query: q });
      setResult(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <section className="py-6 text-center">
        <h1 className="text-3xl font-bold sm:text-4xl">
          What if it played out <span className="text-accent">differently</span>?
        </h1>
        <p className="mx-auto mt-3 max-w-xl text-muted">
          Ask any FIFA World Cup 2026 scenario. See recomputed standings,
          qualification odds, knockout paths and an instant explanation.
        </p>
      </section>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          run(query);
        }}
        className="mx-auto max-w-2xl"
      >
        <div className="flex gap-2">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="What if Brazil loses today?"
            className="flex-1 rounded-xl border border-border bg-surface px-4 py-3 outline-none focus:border-accent"
          />
          <button
            type="submit"
            disabled={loading}
            className="rounded-xl bg-accent px-5 py-3 font-semibold text-background hover:opacity-90 disabled:opacity-50"
          >
            {loading ? "Simulating…" : "Simulate"}
          </button>
        </div>
        <div className="mt-3 flex flex-wrap justify-center gap-2">
          {EXAMPLES.map((ex) => (
            <button
              key={ex}
              type="button"
              onClick={() => {
                setQuery(ex);
                run(ex);
              }}
              className="rounded-full border border-border bg-surface px-3 py-1 text-xs text-muted hover:border-accent hover:text-foreground"
            >
              {ex}
            </button>
          ))}
        </div>
      </form>

      {error && (
        <div className="mx-auto max-w-2xl rounded-lg border border-danger/40 bg-danger/10 px-4 py-2 text-sm text-danger">
          {error}
          <span className="block text-xs text-muted">
            Is the backend running at {api.shareCardUrl().replace("/share-card", "")}?
          </span>
        </div>
      )}

      {result ? (
        <ScenarioResults result={result} baseline={baseline} />
      ) : (
        <Card title="Current title contenders">
          {booting ? (
            <p className="text-sm text-muted">Loading live probabilities…</p>
          ) : (
            <div className="grid gap-3 sm:grid-cols-2">
              {contenders.map((c) => (
                <div key={c.team_id} className="flex items-center gap-3">
                  <div className="w-32 shrink-0">
                    <TeamBadge code={c.fifa_code} name={c.team} teamId={c.team_id} size="sm" />
                  </div>
                  <div className="flex-1">
                    <ProbabilityBar
                      value={c.championship_probability}
                      color="var(--accent-2)"
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>
      )}
    </div>
  );
}
