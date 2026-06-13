// Types mirroring the backend Pydantic schemas.

export interface Team {
  team_id: number;
  name: string;
  fifa_code: string;
  group_name: string;
  flag_url: string;
  rating: number;
}

export interface Match {
  match_id: number;
  home_team_id: number;
  away_team_id: number;
  home_team: string;
  away_team: string;
  home_code: string;
  away_code: string;
  group_name: string;
  matchday: number;
  match_date: string;
  status: string;
  home_goals: number | null;
  away_goals: number | null;
}

export interface StandingRow {
  position: number;
  team_id: number;
  team: string;
  fifa_code: string;
  group_name: string;
  played: number;
  wins: number;
  draws: number;
  losses: number;
  gf: number;
  ga: number;
  gd: number;
  points: number;
  qualification_status: "qualified" | "third" | "out";
}

export interface GroupTable {
  group_name: string;
  rows: StandingRow[];
}

export interface GroupDetail {
  group_name: string;
  teams: Team[];
  table: StandingRow[];
}

export interface TeamProbabilities {
  team_id: number;
  team: string;
  fifa_code: string;
  group_name: string;
  qualification_probability: number;
  group_win_probability: number;
  round_of_16_probability: number;
  quarter_final_probability: number;
  semi_final_probability: number;
  final_probability: number;
  championship_probability: number;
}

export interface KnockoutRound {
  round_name: string;
  opponent_team_id: number | null;
  opponent: string;
  opponent_code: string;
  win_probability: number;
}

export interface KnockoutPath {
  team_id: number;
  team: string;
  seeded_position: string;
  rounds: KnockoutRound[];
}

export interface ScenarioMatch {
  match_id: number;
  home_goals: number;
  away_goals: number;
}

export interface SimulateResponse {
  parsed_query: string | null;
  applied_scenario: ScenarioMatch[];
  updated_standings: GroupTable[];
  qualification_probabilities: TeamProbabilities[];
  knockout_path: KnockoutPath | null;
  ai_summary: string;
}

export interface TeamOutlook {
  team: Team;
  probabilities: TeamProbabilities | null;
  remaining_matches: Match[];
  knockout_path: KnockoutPath | null;
}
