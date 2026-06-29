import {
  BracketResponse,
  Fixture,
  FixtureOddsResponse,
  FixtureStatsResponse,
  FixtureWatchResponse,
  PredictPayload,
  Prediction,
  SyncStatus,
  Team
} from "../types";

const configuredApiBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim();
const API_BASE_URL = configuredApiBaseUrl || (import.meta.env.PROD ? "" : "http://localhost:9000");

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options
  });

  if (!response.ok) {
    const hint =
      import.meta.env.PROD && !configuredApiBaseUrl
        ? " VITE_API_BASE_URL is not configured for this static deployment."
        : "";
    throw new Error(`API request failed: ${response.status}.${hint}`);
  }

  return response.json();
}

function normalizePrediction(prediction: Prediction): Prediction {
  return {
    ...prediction,
    home_team: prediction.home_team ?? prediction.home_team_name ?? "",
    away_team: prediction.away_team ?? prediction.away_team_name ?? "",
    explanation: prediction.explanation ?? prediction.explanation_json ?? []
  };
}

export const getTeams = () => request<Team[]>("/api/teams");
export const getTeam = (id: number) => request<Team>(`/api/teams/${id}`);
export const getFixtures = () => request<Fixture[]>("/api/fixtures");
export const getFixture = (id: number) => request<Fixture>(`/api/fixtures/${id}`);
export const getFixtureOdds = (id: number) => request<FixtureOddsResponse>(`/api/fixtures/${id}/odds`);
export const getFixtureStats = (id: number) => request<FixtureStatsResponse>(`/api/fixtures/${id}/stats`);
export const getFixtureWatchLinks = (id: number) => request<FixtureWatchResponse>(`/api/fixtures/${id}/watch`);
export const getBracket = () => request<BracketResponse>("/api/bracket");
export const getOdds = () => request<unknown[]>("/api/odds");
export const getSyncStatus = () => request<SyncStatus>("/api/sync/status");
export const runManualSync = () => request<unknown>("/api/sync/run", { method: "POST" });
export const getPredictions = async () => {
  const predictions = await request<Prediction[]>("/api/predictions");
  return predictions.map(normalizePrediction);
};
export const getPrediction = async (id: number) => {
  const prediction = await request<Prediction>(`/api/predictions/${id}`);
  return normalizePrediction(prediction);
};
export const predictCustomMatch = (payload: PredictPayload) =>
  request<Prediction>("/api/predict", {
    method: "POST",
    body: JSON.stringify(payload)
  });
