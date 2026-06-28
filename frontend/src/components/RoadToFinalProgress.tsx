const stages = ["Round of 32", "Round of 16", "Quarter-final", "Semi-final", "Final"];

export default function RoadToFinalProgress({ currentStage }: { currentStage?: string | null }) {
  const activeIndex = Math.max(0, stages.findIndex((stage) => stage === currentStage));

  return (
    <section className="border border-white/15 bg-slate-900/80 p-5 shadow-broadcast">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <p className="text-sm font-black uppercase text-yellow-300">Road to the Final</p>
          <p className="mt-1 text-sm text-slate-300">Bracket progression storytelling from first knockout tie to trophy pick.</p>
        </div>
        <div className="grid flex-1 grid-cols-5 gap-2">
          {stages.map((stage, index) => {
            const active = index <= activeIndex;
            return (
              <div key={stage} className="min-w-0">
                <div className={`h-2 rounded-full ${active ? "bg-yellow-300" : "bg-white/15"}`} />
                <p className={`mt-2 truncate text-xs font-bold ${active ? "text-white" : "text-slate-400"}`}>{stage}</p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

