// Typed client for the What-If FIFA Simulator backend.
import type {
  GroupDetail,
  GroupTable,
  Match,
  ScenarioMatch,
  SimulateResponse,
  Team,
  TeamOutlook,
} from "./types";

export const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`GET ${path} failed: ${res.status}`);
  return res.json() as Promise<T>;
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    let detail = `${res.status}`;
    try {
      detail = (await res.json()).detail ?? detail;
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

export const api = {
  teams: () => get<Team[]>("/teams"),
  team: (id: number) => get<Team>(`/teams/${id}`),
  teamOutlook: (id: number) => get<TeamOutlook>(`/teams/${id}/outlook`),
  groups: () => get<GroupDetail[]>("/groups"),
  standings: () => get<GroupTable[]>("/standings"),
  matches: (params?: { group?: string; status?: string }) => {
    const q = new URLSearchParams(params as Record<string, string>).toString();
    return get<Match[]>(`/matches${q ? `?${q}` : ""}`);
  },
  simulate: (body: {
    query?: string;
    scenario?: ScenarioMatch[];
    focus_team_id?: number;
  }) => post<SimulateResponse>("/simulate", body),
  shareCardUrl: () => `${API_URL}/share-card`,
};
