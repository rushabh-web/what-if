import type { TeamProbabilities } from "@/lib/types";
import { ProbabilityBar } from "./ProbabilityBar";

const STAGES: { key: keyof TeamProbabilities; label: string }[] = [
  { key: "qualification_probability", label: "Qualify (R32)" },
  { key: "round_of_16_probability", label: "Round of 16" },
  { key: "quarter_final_probability", label: "Quarter-final" },
  { key: "semi_final_probability", label: "Semi-final" },
  { key: "final_probability", label: "Final" },
  { key: "championship_probability", label: "Champions" },
];

export function ProbabilityFunnel({
  probs,
  baseline,
}: {
  probs: TeamProbabilities;
  baseline?: TeamProbabilities;
}) {
  return (
    <div className="space-y-3">
      {STAGES.map((s) => {
        const value = probs[s.key] as number;
        const base = baseline ? (baseline[s.key] as number) : undefined;
        return (
          <ProbabilityBar
            key={s.key}
            label={s.label}
            value={value}
            delta={base !== undefined ? value - base : undefined}
            color={s.key === "championship_probability" ? "var(--accent-2)" : "var(--accent)"}
          />
        );
      })}
    </div>
  );
}
