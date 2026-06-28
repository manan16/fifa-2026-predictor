interface Props {
  homeTeam: string;
  awayTeam: string;
  predictedHome?: number | null;
  predictedAway?: number | null;
  actualHome?: number | null;
  actualAway?: number | null;
  homePenalties?: number | null;
  awayPenalties?: number | null;
  actualWinner?: string | null;
  status?: string | null;
}

export default function ScoreDisplay({
  homeTeam,
  awayTeam,
  predictedHome,
  predictedAway,
  actualHome,
  actualAway,
  homePenalties,
  awayPenalties,
  actualWinner,
  status
}: Props) {
  const completed = status === "completed" || actualWinner != null || (actualHome != null && actualAway != null);
  const hasPrediction = predictedHome != null && predictedAway != null;
  const hasActual = actualHome != null && actualAway != null;
  const primaryLabel = completed && hasActual ? "Actual score" : "Predicted score";
  const primaryHome = completed && hasActual ? actualHome : predictedHome;
  const primaryAway = completed && hasActual ? actualAway : predictedAway;

  return (
    <div className="text-center">
      <p className="text-xs font-black uppercase tracking-wide text-slate-400">{primaryLabel}</p>
      <div className="mt-2 grid grid-cols-[1fr_auto_1fr] items-center gap-4">
        <p className="truncate text-right text-sm font-bold text-slate-300">{homeTeam}</p>
        <p className="min-w-28 text-center text-5xl font-black text-yellow-300">
          {primaryHome ?? "-"}-{primaryAway ?? "-"}
        </p>
        <p className="truncate text-left text-sm font-bold text-slate-300">{awayTeam}</p>
      </div>
      <p className="mt-2 text-xs text-slate-400">
        {completed && hasActual
          ? hasPrediction
            ? `Predicted: ${predictedHome}-${predictedAway}`
            : "Prediction loading"
          : "Actual: Not played yet"}
      </p>
      {homePenalties != null && awayPenalties != null && (
        <p className="mt-1 text-xs font-bold text-white">
          {actualWinner ?? "Winner"} won {homePenalties}-{awayPenalties} pens
        </p>
      )}
    </div>
  );
}

