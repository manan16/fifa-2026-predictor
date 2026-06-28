interface Props {
  confidence: "Low" | "Medium" | "High";
}

const styles = {
  Low: "bg-orange-500/15 text-orange-300 ring-1 ring-orange-400/25",
  Medium: "bg-yellow-400/15 text-yellow-300 ring-1 ring-yellow-300/25",
  High: "bg-emerald-400/15 text-emerald-300 ring-1 ring-emerald-300/25"
};

export default function ConfidenceBadge({ confidence }: Props) {
  return (
    <span className={`inline-flex px-2.5 py-1 text-xs font-bold ${styles[confidence]}`}>
      {confidence} confidence
    </span>
  );
}
