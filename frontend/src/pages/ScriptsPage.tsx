import { useEffect, useState } from "react";
import { getScripts, scriptLabel, type ScriptsResponse } from "../api";

const MODALITY_LABELS: Record<string, string> = {
  image: "Image",
  video: "Video",
  voice: "Voice",
  model_3d: "3D",
};

export function ScriptsPage(): React.JSX.Element {
  const [data, setData] = useState<ScriptsResponse | null>(null);

  useEffect(() => {
    void getScripts().then(setData);
  }, []);

  if (!data) {
    return <p className="text-zinc-500 text-sm">Loading scripts…</p>;
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold">Scripts</h1>
        <p className="text-zinc-400 text-sm mt-1">CLI entry points grouped by modality</p>
      </div>

      {Object.entries(data.by_modality).map(([modality, scripts]) => (
        <section key={modality}>
          <h2 className="text-sm font-medium text-zinc-400 uppercase tracking-wide mb-3">
            {MODALITY_LABELS[modality] ?? modality}
          </h2>
          <ul className="space-y-2">
            {scripts.map((path) => (
              <li
                key={path}
                className="rounded-xl border border-white/10 bg-white/[0.03] px-4 py-3 flex flex-wrap items-center justify-between gap-2"
              >
                <div>
                  <p className="font-medium">{scriptLabel(path, data.labels)}</p>
                  <p className="text-xs text-zinc-500 font-mono mt-0.5">{path}</p>
              </div>
              <span className="text-xs text-zinc-500">see justfile recipes</span>
              </li>
            ))}
          </ul>
        </section>
      ))}
    </div>
  );
}
