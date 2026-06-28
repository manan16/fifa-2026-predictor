import { useEffect, useState } from "react";
import AnimatedPage from "../components/AnimatedPage";
import { getTeams } from "../services/api";
import { Team } from "../types";

export default function Teams() {
  const [teams, setTeams] = useState<Team[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    getTeams()
      .then(setTeams)
      .catch(() => setError("Unable to load teams."));
  }, []);

  return (
    <AnimatedPage className="space-y-6">
      <div>
        <p className="text-sm font-black uppercase text-gold">Squad strength board</p>
        <h1 className="mt-2 text-3xl font-black text-line">Teams</h1>
        <p className="mt-2 text-line/65">Seeded sample teams with ranking and Elo-style strength inputs.</p>
      </div>
      {error && <div className="border border-coral/30 bg-coral/10 p-4 text-coral">{error}</div>}
      <div className="overflow-x-auto border border-line/10 bg-line/[0.06] shadow-broadcast">
        <table className="w-full min-w-[680px] text-left">
          <thead className="bg-pitch text-line">
            <tr>
              <th className="px-4 py-3">Team</th>
              <th className="px-4 py-3">Code</th>
              <th className="px-4 py-3">Confederation</th>
              <th className="px-4 py-3">FIFA ranking</th>
              <th className="px-4 py-3">Elo rating</th>
            </tr>
          </thead>
          <tbody>
            {teams.map((team) => (
              <tr key={team.id} className="border-b border-line/10 text-line/80">
                <td className="px-4 py-3 font-bold">{team.name}</td>
                <td className="px-4 py-3">{team.fifa_code}</td>
                <td className="px-4 py-3">
                  <span className="border border-gold/25 bg-gold/10 px-2 py-1 text-xs font-black text-gold">
                    {team.confederation}
                  </span>
                </td>
                <td className="px-4 py-3">{team.fifa_ranking}</td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-3">
                    <span className="w-12 font-bold">{team.elo_rating}</span>
                    <div className="h-2 flex-1 overflow-hidden rounded-full bg-line/10">
                      <div
                        className="h-full rounded-full bg-gradient-to-r from-grass to-gold animate-bar-fill"
                        style={{ width: `${Math.min(100, Math.max(20, (team.elo_rating - 1450) / 8))}%` }}
                      />
                    </div>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </AnimatedPage>
  );
}
