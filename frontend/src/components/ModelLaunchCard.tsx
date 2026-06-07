import type { GenerationModelInfo } from "../api";
import { StatusBadge } from "./StatusBadge";

type ModelLaunchCardProps = {
  model: GenerationModelInfo;
  launching: boolean;
  disabled?: boolean;
  onLaunch: (modelId: string) => void;
};

export function ModelLaunchCard({
  model,
  launching,
  disabled = false,
  onLaunch,
}: ModelLaunchCardProps): React.JSX.Element {
  return (
    <article className="rounded-xl border border-white/10 bg-white/[0.03] hover:border-indigo-500/40 hover:bg-white/[0.05] transition-all p-5 flex flex-col gap-4">
      <div className="flex items-start gap-3">
        <span className="text-3xl leading-none" aria-hidden>
          {model.emoji}
        </span>
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="font-semibold">{model.label}</h3>
            <span className="text-[10px] uppercase tracking-wider text-zinc-500 bg-white/5 px-1.5 py-0.5 rounded">
              {model.modality_label}
            </span>
          </div>
          <p className="text-xs text-zinc-500 font-mono mt-1 truncate">{model.model_id}</p>
        </div>
      </div>

      <p className="text-sm text-zinc-400 leading-relaxed flex-1">{model.description}</p>

      <div className="flex flex-wrap items-center justify-between gap-2 pt-1 border-t border-white/5">
        <code className="text-[11px] text-zinc-600">just {model.just_recipe}</code>
        <button
          type="button"
          disabled={launching || disabled}
          onClick={() => onLaunch(model.id)}
          className="px-4 py-2 rounded-lg text-sm font-medium bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {launching ? "Starting…" : "Generate demo"}
        </button>
      </div>
    </article>
  );
}

type ActiveJobBannerProps = {
  label: string;
  status: string;
  error?: string | null;
};

export function ActiveJobBanner({ label, status, error }: ActiveJobBannerProps): React.JSX.Element {
  return (
    <div className="rounded-xl border border-indigo-500/30 bg-indigo-500/10 px-4 py-3 flex flex-wrap items-center justify-between gap-3">
      <div>
        <p className="text-sm font-medium">{label}</p>
        {error ? <p className="text-xs text-red-300 mt-1">{error}</p> : null}
      </div>
      <StatusBadge status={status === "running" ? "running" : status === "completed" ? "completed" : "failed"} />
    </div>
  );
}
