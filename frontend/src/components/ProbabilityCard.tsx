interface Props {
  label: string;
  value: number;
  tone?: "home" | "draw" | "away";
}

const toneClass = {
  home: "border-pitch bg-pitch/5",
  draw: "border-gold bg-gold/10",
  away: "border-coral bg-coral/5"
};

export default function ProbabilityCard({ label, value, tone = "home" }: Props) {
  return (
    <div className={`border-l-4 bg-white p-4 shadow-sm ${toneClass[tone]}`}>
      <p className="text-sm font-semibold text-ink/65">{label}</p>
      <p className="mt-2 text-3xl font-bold">{Math.round(value * 100)}%</p>
    </div>
  );
}

