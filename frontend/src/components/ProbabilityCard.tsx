interface Props {
  label: string;
  value: number;
  tone?: "home" | "draw" | "away";
}

const toneClass = {
  home: "border-emerald-300 bg-slate-900/85",
  draw: "border-yellow-300 bg-slate-900/85",
  away: "border-orange-300 bg-slate-900/85"
};

export default function ProbabilityCard({ label, value, tone = "home" }: Props) {
  return (
    <div className={`border-l-4 p-4 text-slate-100 shadow-broadcast ${toneClass[tone]}`}>
      <p className="text-sm font-semibold text-slate-300">{label}</p>
      <p className="mt-2 text-3xl font-bold text-yellow-300">{Math.round(value * 100)}%</p>
    </div>
  );
}
