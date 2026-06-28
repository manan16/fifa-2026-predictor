interface Props {
  side: "home" | "away";
  name: string;
  code?: string;
  ranking?: number | null;
  elo?: number | null;
}

export default function TeamPanel({ side, name, code, ranking, elo }: Props) {
  return (
    <div className={`flex flex-col items-center gap-3 ${side === "away" ? "lg:text-right" : ""}`}>
      <div className="grid h-20 w-20 place-items-center bg-white/[0.08] text-xl font-black text-white ring-1 ring-white/15 [clip-path:polygon(50%_0,100%_18%,100%_78%,50%_100%,0_78%,0_18%)]">
        {code ?? "TBD"}
      </div>
      <div>
        <p className="text-center text-3xl font-black uppercase leading-none text-white sm:text-4xl">{name}</p>
        <p className="mt-2 text-center text-xs font-bold uppercase tracking-[0.16em] text-slate-400">
          FIFA rank {ranking ?? "TBD"} · Elo {elo ?? "TBD"}
        </p>
      </div>
    </div>
  );
}
