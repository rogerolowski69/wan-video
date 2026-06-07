import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { formatDate, getRun, getScripts, scriptLabel, type Run } from "../api";
import { MediaTile } from "../components/MediaTile";
import { StatusBadge } from "../components/StatusBadge";

export function RunDetailPage(): React.JSX.Element {
  const { id } = useParams<{ id: string }>();
  const [run, setRun] = useState<Run | null>(null);
  const [labels, setLabels] = useState<Record<string, string>>({});
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    let cancelled = false;
    async function load(): Promise<void> {
      try {
        const [runData, scriptsData] = await Promise.all([getRun(Number(id)), getScripts()]);
        if (!cancelled) {
          setRun(runData);
          setLabels(scriptsData.labels);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : "Not found");
      }
    }
    void load();
    return () => {
      cancelled = true;
    };
  }, [id]);

  if (error) {
    return (
      <div className="space-y-4">
        <BackLink />
        <p className="text-red-300">{error}</p>
      </div>
    );
  }

  if (!run) {
    return (
      <div className="space-y-4">
        <BackLink />
        <p className="text-zinc-500">Loading…</p>
      </div>
    );
  }

  const media = run.artifacts.filter((a) => a.kind !== "json");
  const meta = run.artifacts.filter((a) => a.kind === "json");

  return (
    <div className="space-y-8">
      <BackLink />

      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">{scriptLabel(run.script, labels)}</h1>
          <p className="text-zinc-500 text-sm mt-1">
            Run #{run.id} · {run.model}
          </p>
        </div>
        <StatusBadge status={run.status} />
      </div>

      <dl className="grid sm:grid-cols-2 gap-4 text-sm">
        <Field label="Started" value={formatDate(run.started_at)} />
        <Field label="Completed" value={run.completed_at ? formatDate(run.completed_at) : "—"} />
        <Field label="Backend" value={run.backend} />
        <Field label="Provider" value={run.provider ?? "—"} />
      </dl>

      {run.prompt ? (
        <div className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
          <p className="text-xs text-zinc-500 mb-2 uppercase tracking-wide">Prompt</p>
          <p className="text-sm leading-relaxed text-zinc-300">{run.prompt}</p>
        </div>
      ) : null}

      {run.error ? (
        <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-200">
          {run.error}
        </div>
      ) : null}

      {media.length > 0 ? (
        <section>
          <h2 className="text-lg font-medium mb-4">Outputs</h2>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {media.map((item) => (
              <MediaTile key={item.path} item={item} />
            ))}
          </div>
        </section>
      ) : null}

      {meta.length > 0 ? (
        <section>
          <h2 className="text-lg font-medium mb-4">Metadata</h2>
          <ul className="space-y-2">
            {meta.map((item) => (
              <li key={item.path}>
                <a href={item.url} className="text-sm text-indigo-400 hover:underline">
                  {item.path.split("/").pop()}
                </a>
              </li>
            ))}
          </ul>
        </section>
      ) : null}
    </div>
  );
}

function BackLink(): React.JSX.Element {
  return (
    <Link to="/" className="text-sm text-zinc-400 hover:text-zinc-200">
      ← All runs
    </Link>
  );
}

function Field({ label, value }: { label: string; value: string }): React.JSX.Element {
  return (
    <div className="rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2">
      <dt className="text-xs text-zinc-500">{label}</dt>
      <dd className="mt-0.5 font-medium">{value}</dd>
    </div>
  );
}
