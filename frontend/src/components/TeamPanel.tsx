import { CSSProperties } from "react";
import { flagUrl } from "../lib/flags";

interface Props {
  side: "home" | "away";
  name: string;
  code?: string;
  ranking?: number | null;
  elo?: number | null;
}

const HEX_CLIP = "polygon(50% 0, 100% 18%, 100% 78%, 50% 100%, 0 78%, 0 18%)";

export default function TeamPanel({ side, name, code, ranking, elo }: Props) {
  const flag = flagUrl(code);
  const style: CSSProperties = {
    clipPath: HEX_CLIP,
    ...(flag ? { backgroundImage: `url(${flag})`, backgroundSize: "cover", backgroundPosition: "center" } : {}),
  };

  return (
    <div className={`flex flex-col items-center gap-3 ${side === "away" ? "lg:text-right" : ""}`}>
      <div
        style={style}
        className={`grid h-20 w-20 place-items-center text-xl font-black text-white ring-1 ring-white/15 ${
          flag ? "" : "bg-white/[0.08]"
        }`}
      >
        {!flag && (code ?? "TBD")}
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