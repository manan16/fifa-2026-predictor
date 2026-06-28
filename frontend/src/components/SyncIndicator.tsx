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
  idle: "text-chalk-dim",
  syncing: "text-gold",
  synced: "text-sky",
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
        <span className="font-mono text-xs font-bold uppercase tracking-[0.12em] text-chalk">{label[phase]}</span>
        <span className="font-mono text-[10px] uppercase text-chalk-dim">· auto</span>
      </div>
      <p className="mt-2 text-sm text-chalk-dim">
        {detail}
        {phase !== "syncing" && (
          <span className="text-chalk-dim"> · updated {timeAgo(lastTime)}</span>
        )}
      </p>
      <div className="sync-track mt-3 h-1 w-full overflow-hidden rounded-full bg-chalk-faint">
        {phase !== "syncing" && (
          <div
            className={`h-full rounded-full ${phase === "error" ? "bg-coral/70" : "bg-sky/70"}`}
            style={{ width: "100%" }}
          />
        )}
      </div>
    </div>
  );
}
