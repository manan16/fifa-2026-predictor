interface Props {
  label: string;
  value?: number | null;
  variant?: "model" | "market" | "blended";
}

const styles = {
  model: "from-grass to-gold",
  market: "from-sky-400 to-line",
  blended: "from-gold to-coral"
};

export default function ProbabilityBar({ label, value, variant = "model" }: Props) {
  const pct = value == null ? 0 : Math.max(0, Math.min(100, Math.round(value * 100)));

  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-xs font-bold uppercase text-white/65">
        <span>{label}</span>
        <span>{value == null ? "TBD" : `${pct}%`}</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-white/10">
        <div
          className={`h-full rounded-full bg-gradient-to-r ${styles[variant]} animate-bar-fill`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
