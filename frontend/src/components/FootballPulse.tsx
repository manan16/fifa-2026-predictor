interface Props {
  status?: string | null;
}

export default function FootballPulse({ status }: Props) {
  const normalized = (status ?? "scheduled").toLowerCase();
  const completed = normalized === "completed";
  const live = normalized === "live";

  return (
    <span className="relative inline-flex h-3 w-3 items-center justify-center" aria-label={normalized}>
      {!completed && (
        <span
          className={`absolute h-3 w-3 rounded-full ${live ? "bg-coral" : "bg-gold"} animate-pulse-dot opacity-70`}
        />
      )}
      <span className={`relative h-2 w-2 rounded-full ${completed ? "bg-white/45" : live ? "bg-coral" : "bg-gold"}`} />
    </span>
  );
}

