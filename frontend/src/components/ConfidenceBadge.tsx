interface Props {
  confidence: "Low" | "Medium" | "High";
}

const styles = {
  Low: "bg-coral/15 text-coral",
  Medium: "bg-gold/20 text-ink",
  High: "bg-pitch/15 text-pitch"
};

export default function ConfidenceBadge({ confidence }: Props) {
  return (
    <span className={`inline-flex px-2.5 py-1 text-xs font-bold ${styles[confidence]}`}>
      {confidence} confidence
    </span>
  );
}

