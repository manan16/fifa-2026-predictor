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
  predicted_home_goals?: number | null;
  predicted_away_goals?: number | null;
  actual_home_score?: number | null;
  actual_away_score?: number | null;
  home_penalties?: number | null;
  away_penalties?: number | null;
  predicted_winner?: string | null;
  actual_winner?: string | null;
  winner_team_id?: number | null;
  market_home_probability?: number | null;
  market_draw_probability?: number | null;
  market_away_probability?: number | null;
  average_home_odds?: number | null;
  average_draw_odds?: number | null;
  average_away_odds?: number | null;
  best_home_odds?: number | null;
  best_draw_odds?: number | null;
  best_away_odds?: number | null;
  bookmaker_count?: number | null;
  last_odds_sync?: string | null;
  last_result_sync?: string | null;
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

export interface BookmakerOdds {
  bookmaker: string;
  region: string | null;
  market_key: string;
  outcome_name: string;
  outcome_type: "home" | "draw" | "away" | "over" | "under" | "outright";
  decimal_price: number | null;
  implied_probability: number | null;
  normalized_probability: number | null;
  last_update: string | null;
  source?: string;
}

export interface OddsConsensus {
  fixture_id?: number;
  market_key?: string;
  home_probability: number | null;
  draw_probability: number | null;
  away_probability: number | null;
  average_home_odds: number | null;
  average_draw_odds: number | null;
  average_away_odds: number | null;
  best_home_odds: number | null;
  best_draw_odds: number | null;
  best_away_odds: number | null;
  bookmaker_count: number | null;
  calculated_at: string | null;
  source?: string;
}

export interface FixtureOddsResponse {
  fixture: Fixture;
  odds: BookmakerOdds[];
  consensus: OddsConsensus | null;
}

export interface SyncRun {
  id?: number;
  job_name: string;
  status: string;
  started_at?: string;
  finished_at?: string | null;
  message?: string | null;
  records_processed?: number;
}

export interface SyncStatus {
  latest_runs: SyncRun[];
  last_run: SyncRun | null;
}

export type BracketRoundKey =
  | "round_of_32"
  | "round_of_16"
  | "quarter_finals"
  | "semi_finals"
  | "final";

export interface BracketFixture {
  id: number;
  match_number: number;
  stage: string;
  group_name: "Left bracket" | "Right bracket" | "Champion pick" | string | null;
  status: string;
  home_team_name: string;
  away_team_name: string;
  home_team_code: string;
  away_team_code: string;
  kickoff_time: string;
  predicted_winner: string;
  home_win_probability: number | null;
  draw_probability: number | null;
  away_win_probability: number | null;
  home_advance_probability: number | null;
  away_advance_probability: number | null;
  predicted_home_goals: number | null;
  predicted_away_goals: number | null;
  actual_home_score: number | null;
  actual_away_score: number | null;
  home_penalties: number | null;
  away_penalties: number | null;
  actual_winner: string | null;
  market_home_probability: number | null;
  market_draw_probability: number | null;
  market_away_probability: number | null;
  average_home_odds: number | null;
  average_draw_odds: number | null;
  average_away_odds: number | null;
  best_home_odds: number | null;
  best_draw_odds: number | null;
  best_away_odds: number | null;
  bookmaker_count: number | null;
  last_odds_sync?: string | null;
  last_result_sync?: string | null;
  confidence: "Low" | "Medium" | "High" | null;
}

export type BracketResponse = Record<BracketRoundKey, BracketFixture[]>;
