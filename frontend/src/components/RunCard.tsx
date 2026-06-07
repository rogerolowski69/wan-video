import { Link } from "react-router-dom";
import type { Run } from "../api";
import { formatDate, scriptLabel } from "../api";
import { StatusBadge } from "./StatusBadge";

type RunCardProps = {
  run: Run;
  labels?: Record<string, string>;
};

export function RunCard({ run, labels }: RunCardProps): React.JSX.Element {
  const media = run.artifacts.filter((a) => a.kind !== "json");
  const thumb = media.find((a) => a.kind === "image") ?? media[0];

  return (
    <Link
      to={`/runs/${run.id}`}
      className="group block rounded-xl border border-white/10 bg-white/[0.03] hover:bg-white/[0.06] hover:border-indigo-500/30 transition-all overflow-hidden"
    >
      <div className="aspect-video bg-zinc-900/80 relative overflow-hidden">
        {thumb?.kind === "image" ? (
          <img
            src={thumb.url}
            alt=""
            className="w-full h-full object-cover group-hover:scale-[1.02] transition-transform duration-300"
            loading="lazy"
          />
        ) : thumb?.kind === "video" ? (
          <video src={thumb.url} className="w-full h-full object-cover" muted preload="metadata" />
        ) : (
          <div className="flex items-center justify-center h-full text-zinc-600 text-sm">
            {media.length ? `${media.length} file(s)` : "No preview"}
          </div>
        )}
        <div className="absolute top-2 right-2">
          <StatusBadge status={run.status} />
        </div>
      </div>
      <div className="p-4 space-y-2">
        <div className="flex items-center justify-between gap-2">
          <h3 className="font-medium text-sm truncate">{scriptLabel(run.script, labels)}</h3>
          <span className="text-xs text-zinc-500 shrink-0">#{run.id}</span>
        </div>
        <p className="text-xs text-zinc-500 truncate">{run.model}</p>
        {run.prompt ? (
          <p className="text-xs text-zinc-400 line-clamp-2 leading-relaxed">{run.prompt}</p>
        ) : null}
        <p className="text-xs text-zinc-600">{formatDate(run.started_at)}</p>
      </div>
    </Link>
  );
}
