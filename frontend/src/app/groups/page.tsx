"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { GroupDetail } from "@/lib/types";
import { StandingsTable } from "@/components/StandingsTable";

export default function GroupsPage() {
  const [groups, setGroups] = useState<GroupDetail[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .groups()
      .then(setGroups)
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold">Group Explorer</h1>
        <p className="text-sm text-muted">
          Live standings across all 12 groups. Top two qualify (green); the eight
          best third-placed teams (blue) also advance.
        </p>
      </div>

      {error && (
        <div className="rounded-lg border border-danger/40 bg-danger/10 px-4 py-2 text-sm text-danger">
          {error}
        </div>
      )}
      {loading && <p className="text-sm text-muted">Loading groups…</p>}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {groups.map((g) => (
          <StandingsTable
            key={g.group_name}
            table={{ group_name: g.group_name, rows: g.table }}
          />
        ))}
      </div>
    </div>
  );
}
