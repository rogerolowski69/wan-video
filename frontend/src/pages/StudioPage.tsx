import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  getCatalog,
  getHealth,
  getJob,
  getRuns,
  launchModel,
  launchRunAll,
  type CatalogResponse,
  type GenerationModelInfo,
  type Job,
  type Run,
} from "../api";
import { ActiveJobBanner, ModelLaunchCard } from "../components/ModelLaunchCard";
import { LoginGate } from "../components/AuthBar";
import { RunCard } from "../components/RunCard";
import { StatusBadge } from "../components/StatusBadge";

export function StudioPage(): React.JSX.Element {
  const [catalog, setCatalog] = useState<CatalogResponse | null>(null);
  const [runs, setRuns] = useState<Run[]>([]);
  const [health, setHealth] = useState<string>("…");
  const [storage, setStorage] = useState<string>("…");
  const [activeJob, setActiveJob] = useState<Job | null>(null);
  const [launchingId, setLaunchingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    const [catalogData, runsData, healthData] = await Promise.all([
      getCatalog(),
      getRuns(12),
      getHealth(),
    ]);
    setCatalog(catalogData);
    setRuns(runsData);
    setHealth(healthData.status);
    setStorage(healthData.storage);
  }, []);

  useEffect(() => {
    void refresh().catch((err: unknown) => {
      setError(err instanceof Error ? err.message : "Failed to load");
    });
    const timer = setInterval(() => void refresh(), 15_000);
    return () => clearInterval(timer);
  }, [refresh]);

  useEffect(() => {
    if (!activeJob || activeJob.status !== "running") return;
    const timer = setInterval(() => {
      void getJob(activeJob.job_id)
        .then(setActiveJob)
        .then(() => refresh());
    }, 3000);
    return () => clearInterval(timer);
  }, [activeJob, refresh]);

  async function handleLaunch(modelId: string): Promise<void> {
    if (activeJob?.status === "running") return;
    setLaunchingId(modelId);
    setError(null);
    try {
      const job = await launchModel(modelId, { demo: true });
      setActiveJob(job);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Launch failed");
    } finally {
      setLaunchingId(null);
    }
  }

  async function handleRunAll(): Promise<void> {
    if (activeJob?.status === "running") return;
    setLaunchingId("run-all");
    setError(null);
    try {
      const job = await launchRunAll(true);
      setActiveJob(job);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Launch failed");
    } finally {
      setLaunchingId(null);
    }
  }

  const modelsByModality = groupByModality(catalog?.models ?? []);

  const activeJobLabel =
    activeJob?.model_id === "run-all"
      ? "Batch run-all"
      : (catalog?.models.find((m) => m.id === activeJob?.model_id)?.label ?? activeJob?.model_id);

  return (
    <LoginGate>
    <div className="space-y-10">
      <section className="text-center space-y-4 py-4">
        <h1 className="text-3xl sm:text-4xl font-bold tracking-tight bg-gradient-to-r from-indigo-200 via-white to-violet-200 bg-clip-text text-transparent">
          Generation Studio
        </h1>
        <p className="text-zinc-400 max-w-xl mx-auto text-sm sm:text-base">
          Launch any model from one place — fal.ai images, video, 3D, voice, and Wan via Hugging Face.
        </p>
        <div className="flex flex-wrap justify-center gap-3 text-sm">
          <div className="rounded-lg border border-white/10 px-3 py-1.5 bg-white/[0.03]">
            API <StatusBadge status={health === "ok" ? "completed" : "failed"} />
          </div>
          <div className="rounded-lg border border-white/10 px-3 py-1.5 text-zinc-400">
            Storage: <span className="text-zinc-200">{storage}</span>
          </div>
          <button
            type="button"
            onClick={() => void handleRunAll()}
            disabled={launchingId === "run-all" || activeJob?.status === "running"}
            className="rounded-lg border border-violet-500/40 bg-violet-500/15 px-4 py-1.5 text-violet-200 hover:bg-violet-500/25 disabled:opacity-50 transition-colors"
          >
            {launchingId === "run-all" ? "Starting batch…" : "🚀 Run all (demo)"}
          </button>
        </div>
      </section>

      {error ? (
        <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-200">
          {error}
        </div>
      ) : null}

      {activeJob ? (
        <ActiveJobBanner
          label={
            activeJob.status === "running"
              ? `${activeJobLabel} — generating…`
              : `${activeJobLabel} — ${activeJob.status}`
          }
          status={activeJob.status}
          error={activeJob.error}
        />
      ) : null}

      {Object.entries(modelsByModality).map(([modality, models]) => (
        <section key={modality}>
          <h2 className="text-sm font-medium text-zinc-400 uppercase tracking-wide mb-4">
            {catalog?.modality_labels[modality] ?? modality}
          </h2>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {models.map((model) => (
              <ModelLaunchCard
                key={model.id}
                model={model}
                launching={launchingId === model.id}
                disabled={activeJob?.status === "running"}
                onLaunch={(id) => void handleLaunch(id)}
              />
            ))}
          </div>
        </section>
      ))}

      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-medium">Recent runs</h2>
          <Link to="/runs" className="text-sm text-indigo-400 hover:text-indigo-300">
            View all →
          </Link>
        </div>
        {runs.length === 0 ? (
          <p className="text-zinc-500 text-sm">No runs yet — pick a model above to generate.</p>
        ) : (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {runs.slice(0, 6).map((run) => (
              <RunCard key={run.id} run={run} labels={catalog?.labels} />
            ))}
          </div>
        )}
      </section>

      <p className="text-center text-xs text-zinc-600">
        Interactive prompts: run <code className="text-zinc-400">just menu</code> or{" "}
        <code className="text-zinc-400">just flux</code> in your terminal.
      </p>
    </div>
    </LoginGate>
  );
}

function groupByModality(models: GenerationModelInfo[]): Record<string, GenerationModelInfo[]> {
  const grouped: Record<string, GenerationModelInfo[]> = {};
  for (const model of models) {
    grouped[model.modality] ??= [];
    grouped[model.modality].push(model);
  }
  return grouped;
}
