import { useEffect, useState } from "react";
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
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-black">Teams</h1>
        <p className="mt-2 text-ink/65">Seeded sample teams with ranking and Elo-style strength inputs.</p>
      </div>
      {error && <div className="border border-coral/30 bg-coral/10 p-4 text-coral">{error}</div>}
      <div className="overflow-x-auto bg-white shadow-sm">
        <table className="w-full min-w-[680px] text-left">
          <thead className="bg-pitch text-white">
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
              <tr key={team.id} className="border-b border-ink/10">
                <td className="px-4 py-3 font-bold">{team.name}</td>
                <td className="px-4 py-3">{team.fifa_code}</td>
                <td className="px-4 py-3">{team.confederation}</td>
                <td className="px-4 py-3">{team.fifa_ranking}</td>
                <td className="px-4 py-3">{team.elo_rating}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

