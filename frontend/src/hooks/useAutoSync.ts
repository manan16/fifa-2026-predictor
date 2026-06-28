import { useCallback, useEffect, useRef, useState } from "react";
import { getSyncStatus, runManualSync } from "../services/api";
import { SyncStatus } from "../types";

export type SyncPhase = "idle" | "syncing" | "synced" | "error";

interface Options {
  /** How often to refresh the status from the backend. */
  pollMs?: number;
  /** How often this client triggers a full sync itself (belt-and-braces for
   *  setups without the backend scheduler). */
  syncEveryMs?: number;
  /** Trigger a sync immediately on mount when no successful run exists. */
  syncOnMount?: boolean;
}

interface Result {
  status: SyncStatus | null;
  phase: SyncPhase;
}

/**
 * Keeps sync status fresh and runs syncs automatically — no button required.
 * The backend scheduler does the heavy lifting when enabled; this hook also
 * triggers periodic syncs from the client so the dashboard stays live even in
 * a plain local setup.
 */
export function useAutoSync({
  pollMs = 30_000,
  syncEveryMs = 5 * 60_000,
  syncOnMount = true
}: Options = {}): Result {
  const [status, setStatus] = useState<SyncStatus | null>(null);
  const [phase, setPhase] = useState<SyncPhase>("idle");
  const inFlight = useRef(false);

  const refreshStatus = useCallback(async () => {
    try {
      setStatus(await getSyncStatus());
    } catch {
      /* status is best-effort; ignore transient failures */
    }
  }, []);

  const triggerSync = useCallback(async () => {
    if (inFlight.current) return;
    inFlight.current = true;
    setPhase("syncing");
    try {
      await runManualSync();
      await refreshStatus();
      setPhase("synced");
    } catch {
      setPhase("error");
    } finally {
      inFlight.current = false;
    }
  }, [refreshStatus]);

  useEffect(() => {
    let cancelled = false;

    (async () => {
      await refreshStatus();
      if (cancelled) return;
      if (syncOnMount) {
        // Sync now; refreshStatus already ran so the indicator shows context.
        void triggerSync();
      }
    })();

    const pollId = window.setInterval(refreshStatus, pollMs);
    const syncId = window.setInterval(triggerSync, syncEveryMs);

    return () => {
      cancelled = true;
      window.clearInterval(pollId);
      window.clearInterval(syncId);
    };
  }, [refreshStatus, triggerSync, pollMs, syncEveryMs, syncOnMount]);

  return { status, phase };
}
