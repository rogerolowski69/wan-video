import { useEffect, useState } from "react";
import { getHealth, getRuns, getScripts, type Run } from "../api";
import { RunCard } from "../components/RunCard";
import { StatusBadge } from "../components/StatusBadge";

export function DashboardPage(): React.JSX.Element {
  const [runs, setRuns] = useState<Run[]>([]);
  const [labels, setLabels] = useState<Record<string, string>>({});
  const [health, setHealth] = useState<string>("…");
  const [storage, setStorage] = useState<string>("…");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    async function load(): Promise<void> {
      try {
        const [runsData, scriptsData, healthData] = await Promise.all([
          getRuns(50),
          getScripts(),
          getHealth(),
        ]);
        if (cancelled) return;
        setRuns(runsData);
        setLabels(scriptsData.labels);
        setHealth(healthData.status);
        setStorage(healthData.storage);
        setError(null);
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : "Failed to load");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    void load();
    const timer = setInterval(() => void load(), 30_000);
    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, []);

  const completed = runs.filter((r) => r.status === "completed").length;
  const failed = runs.filter((r) => r.status === "failed").length;

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Generation runs</h1>
          <p className="text-zinc-400 text-sm mt-1">History from fal.ai and Hugging Face inference</p>
        </div>
        <div className="flex gap-3 text-sm">
          <div className="rounded-lg border border-white/10 px-3 py-2 bg-white/[0.03]">
            API <StatusBadge status={health === "ok" ? "completed" : "failed"} />
          </div>
          <div className="rounded-lg border border-white/10 px-3 py-2 bg-white/[0.03] text-zinc-400">
            Storage: <span className="text-zinc-200">{storage}</span>
          </div>
        </div>
      </div>

      {!loading && (
        <div className="grid grid-cols-3 gap-3 max-w-md">
          <Stat label="Total" value={String(runs.length)} />
          <Stat label="Completed" value={String(completed)} />
          <Stat label="Failed" value={String(failed)} />
        </div>
      )}

      {error ? (
        <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-200">
          {error} — is the API running?
        </div>
      ) : null}

      {loading ? (
        <p className="text-zinc-500 text-sm">Loading runs…</p>
      ) : runs.length === 0 ? (
        <div className="rounded-xl border border-dashed border-white/15 p-12 text-center text-zinc-500">
          No runs yet. Execute a script with <code className="text-indigo-300">just demo-flux</code> or{" "}
          <code className="text-indigo-300">just run-all</code>.
        </div>
      ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {runs.map((run) => (
            <RunCard key={run.id} run={run} labels={labels} />
          ))}
        </div>
      )}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }): React.JSX.Element {
  return (
    <div className="rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2">
      <p className="text-xs text-zinc-500">{label}</p>
      <p className="text-lg font-semibold">{value}</p>
    </div>
  );
}
