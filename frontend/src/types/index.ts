export interface Team {
  id: number;
  name: string;
  fifa_code: string;
  confederation: string;
  fifa_ranking: number;
  elo_rating: number;
}

export interface Fixture {
  id: number;
  match_number: number;
  stage: string;
  group_name: string | null;
  home_team_id: number;
  away_team_id: number;
  venue: string;
  city: string;
  kickoff_time: string;
  status: string;
  home_team_name: string;
  away_team_name: string;
  home_team_code?: string;
  away_team_code?: string;
  home_team_elo?: number;
  away_team_elo?: number;
}

export interface Prediction {
  id?: number;
  fixture_id?: number;
  model_version?: string;
  home_team: string;
  away_team: string;
  home_team_name?: string;
  away_team_name?: string;
  home_win_probability: number;
  draw_probability: number;
  away_win_probability: number;
  predicted_home_goals: number;
  predicted_away_goals: number;
  confidence: "Low" | "Medium" | "High";
  explanation: string[];
  explanation_json?: string[];
  home_advance_probability?: number;
  away_advance_probability?: number;
}

export interface PredictPayload {
  home_team: string;
  away_team: string;
  neutral_venue: boolean;
  stage: string;
}

