import { BracketFixture } from "../types";
import BracketMatchCard from "./BracketMatchCard";

interface Props {
  title: string;
  fixtures: BracketFixture[];
  direction?: "left" | "right";
  delay?: number;
}

export default function BracketRound({ title, fixtures, direction = "left", delay = 0 }: Props) {
  return (
    <section
      className={`relative flex w-72 shrink-0 flex-col gap-4 ${direction === "left" ? "animate-round-left" : "animate-round-right"}`}
      style={{ animationDelay: `${delay}ms` }}
    >
      <h2 className="text-center text-sm font-black uppercase tracking-wide text-slate-300">{title}</h2>
      <div className="relative flex flex-col gap-4 before:pointer-events-none before:absolute before:left-full before:top-8 before:hidden before:h-[calc(100%-4rem)] before:w-6 before:border-y before:border-r before:border-white/15 md:before:block">
        {fixtures.map((fixture, index) => (
          <div key={fixture.id} className="animate-card-in" style={{ animationDelay: `${delay + index * 55}ms` }}>
            <BracketMatchCard fixture={fixture} />
          </div>
        ))}
        {fixtures.length === 0 && (
          <div className="w-64 border border-dashed border-line/15 p-4 text-center text-sm text-slate-400">TBD</div>
        )}
      </div>
    </section>
  );
}
