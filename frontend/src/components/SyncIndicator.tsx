import { SyncStatus } from "../types";
import { SyncPhase } from "../hooks/useAutoSync";

interface Props {
  status: SyncStatus | null;
  phase: SyncPhase;
}

function timeAgo(iso?: string | null): string {
  if (!iso) return "not yet";
  const then = new Date(iso).getTime();
  if (Number.isNaN(then)) return "not yet";
  const seconds = Math.max(0, Math.round((Date.now() - then) / 1000));
  if (seconds < 60) return `${seconds}s ago`;
  const minutes = Math.round(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.round(minutes / 60);
  return `${hours}h ago`;
}

const dotColour: Record<SyncPhase, string> = {
  idle: "text-line/50",
  syncing: "text-gold",
  synced: "text-grass",
  error: "text-coral"
};

const label: Record<SyncPhase, string> = {
  idle: "Standing by",
  syncing: "Syncing",
  synced: "Live",
  error: "Sync issue"
};

export default function SyncIndicator({ status, phase }: Props) {
  const last = status?.last_run;
  const lastTime = last?.finished_at ?? last?.started_at;
  const detail =
    phase === "syncing"
      ? "Refreshing odds and results…"
      : last?.message ?? "Demo odds mode works without API keys.";

  return (
    <div className="min-w-[220px]">
      <div className="flex items-center gap-2">
        <span className={`live-dot ${dotColour[phase]}`} style={{ backgroundColor: "currentColor" }} />
        <span className="text-sm font-black uppercase tracking-wide text-line">{label[phase]}</span>
        <span className="text-xs font-bold text-line/45">· auto</span>
      </div>
      <p className="mt-2 text-sm text-line/60">
        {detail}
        {phase !== "syncing" && (
          <span className="text-line/45"> · updated {timeAgo(lastTime)}</span>
        )}
      </p>
      <div className="sync-track mt-3 h-1 w-full overflow-hidden rounded-full bg-line/10">
        {phase !== "syncing" && (
          <div
            className={`h-full rounded-full ${phase === "error" ? "bg-coral/70" : "bg-grass/70"}`}
            style={{ width: "100%" }}
          />
        )}
      </div>
    </div>
  );
}
