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
  home_win_probability?: number | null;
  draw_probability?: number | null;
  away_win_probability?: number | null;
  confidence?: "Low" | "Medium" | "High" | null;
  model_version?: string | null;
  prediction_created_at?: string | null;
  average_home_odds?: number | null;
  average_draw_odds?: number | null;
  average_away_odds?: number | null;
  best_home_odds?: number | null;
  best_draw_odds?: number | null;
  best_away_odds?: number | null;
  bookmaker_count?: number | null;
  expected_home_goals?: number | null;
  expected_away_goals?: number | null;
  home_shots?: number | null;
  away_shots?: number | null;
  home_shots_on_target?: number | null;
  away_shots_on_target?: number | null;
  home_possession?: number | null;
  away_possession?: number | null;
  home_corners?: number | null;
  away_corners?: number | null;
  home_yellow_cards?: number | null;
  away_yellow_cards?: number | null;
  home_red_card_probability?: number | null;
  away_red_card_probability?: number | null;
  both_teams_to_score_probability?: number | null;
  over_2_5_goals_probability?: number | null;
  clean_sheet_home_probability?: number | null;
  clean_sheet_away_probability?: number | null;
  last_odds_sync?: string | null;
  last_result_sync?: string | null;
  home_team_name: string;
  away_team_name: string;
  home_team_code?: string;
  away_team_code?: string;
  home_team_ranking?: number | null;
  away_team_ranking?: number | null;
  home_team_elo?: number;
  away_team_elo?: number;
}

export interface PredictedMatchStats {
  fixture_id?: number;
  model_version?: string | null;
  expected_home_goals: number;
  expected_away_goals: number;
  home_shots: number;
  away_shots: number;
  home_shots_on_target: number;
  away_shots_on_target: number;
  home_possession: number;
  away_possession: number;
  home_corners: number;
  away_corners: number;
  home_yellow_cards: number;
  away_yellow_cards: number;
  home_red_card_probability: number;
  away_red_card_probability: number;
  both_teams_to_score_probability: number;
  over_2_5_goals_probability: number;
  clean_sheet_home_probability: number;
  clean_sheet_away_probability: number;
  explanation_json?: string[];
  created_at?: string;
}

export interface ActualMatchStats {
  fixture_id?: number;
  home_shots: number | null;
  away_shots: number | null;
  home_shots_on_target: number | null;
  away_shots_on_target: number | null;
  home_possession: number | null;
  away_possession: number | null;
  home_corners: number | null;
  away_corners: number | null;
  home_yellow_cards: number | null;
  away_yellow_cards: number | null;
  home_red_cards: number | null;
  away_red_cards: number | null;
  source?: string | null;
  last_sync?: string | null;
  created_at?: string;
}

export interface FixtureStatsResponse {
  fixture_id: number;
  predicted: PredictedMatchStats | null;
  actual: ActualMatchStats | null;
  predicted_stats: PredictedMatchStats | null;
  actual_stats: ActualMatchStats | null;
  note: string;
}

export interface WatchLink {
  id?: number;
  fixture_id?: number;
  region: string;
  provider_name: string;
  provider_type: string;
  url: string;
  is_official: boolean;
  note?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface FixtureWatchResponse {
  fixture_id: number;
  links: WatchLink[];
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
  predicted_stats?: PredictedMatchStats;
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
  expected_home_goals?: number | null;
  expected_away_goals?: number | null;
  home_shots?: number | null;
  away_shots?: number | null;
  home_shots_on_target?: number | null;
  away_shots_on_target?: number | null;
  home_possession?: number | null;
  away_possession?: number | null;
  home_corners?: number | null;
  away_corners?: number | null;
  home_yellow_cards?: number | null;
  away_yellow_cards?: number | null;
  home_red_card_probability?: number | null;
  away_red_card_probability?: number | null;
  both_teams_to_score_probability?: number | null;
  over_2_5_goals_probability?: number | null;
  clean_sheet_home_probability?: number | null;
  clean_sheet_away_probability?: number | null;
  last_odds_sync?: string | null;
  last_result_sync?: string | null;
  confidence: "Low" | "Medium" | "High" | null;
}

export type BracketResponse = Record<BracketRoundKey, BracketFixture[]>;
