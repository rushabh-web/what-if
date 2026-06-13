"use client";

import { useState } from "react";
import { api } from "@/lib/api";

export function ShareButton({
  scenarioText,
  team,
  before,
  after,
  opponent,
}: {
  scenarioText: string;
  team: string;
  before: number;
  after: number;
  opponent?: string;
}) {
  const [loading, setLoading] = useState(false);

  async function generate() {
    setLoading(true);
    try {
      const res = await fetch(api.shareCardUrl(), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          scenario_text: scenarioText,
          team,
          before_probability: before,
          after_probability: after,
          most_likely_opponent: opponent ?? "",
        }),
      });
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      window.open(url, "_blank");
    } finally {
      setLoading(false);
    }
  }

  return (
    <button
      onClick={generate}
      disabled={loading}
      className="inline-flex items-center gap-2 rounded-lg border border-border bg-surface-2 px-3 py-1.5 text-sm font-medium hover:border-accent disabled:opacity-50"
    >
      {loading ? "Generating…" : "🖼️ Share card"}
    </button>
  );
}
