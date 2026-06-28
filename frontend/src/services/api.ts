import { Fixture, PredictPayload, Prediction, Team } from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:5000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
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

