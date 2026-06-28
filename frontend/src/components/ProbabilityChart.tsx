import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

interface Props {
  homeTeam: string;
  awayTeam: string;
  home: number;
  draw: number;
  away: number;
}

export default function ProbabilityChart({ homeTeam, awayTeam, home, draw, away }: Props) {
  const data = [
    { outcome: homeTeam, probability: Math.round(home * 100) },
    { outcome: "Draw", probability: Math.round(draw * 100) },
    { outcome: awayTeam, probability: Math.round(away * 100) }
  ];

  return (
    <div className="h-72 bg-white p-4 shadow-sm">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="outcome" />
          <YAxis domain={[0, 100]} tickFormatter={(value) => `${value}%`} />
          <Tooltip formatter={(value) => `${value}%`} />
          <Bar dataKey="probability" fill="#0f6b4b" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

