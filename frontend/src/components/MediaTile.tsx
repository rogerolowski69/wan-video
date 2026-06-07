import type { Artifact, GalleryItem } from "../api";
import { formatBytes } from "../api";

type MediaTileProps = {
  item: Pick<GalleryItem | Artifact, "url" | "kind" | "path" | "size_bytes">;
  subtitle?: string;
};

export function MediaTile({ item, subtitle }: MediaTileProps): React.JSX.Element {
  const name = item.path.split("/").pop() ?? item.path;

  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.03] overflow-hidden">
      <div className="aspect-square bg-zinc-900/80 flex items-center justify-center overflow-hidden">
        {item.kind === "image" ? (
          <img src={item.url} alt={name} className="w-full h-full object-cover" loading="lazy" />
        ) : item.kind === "video" ? (
          <video src={item.url} controls className="w-full h-full object-contain bg-black" preload="metadata" />
        ) : item.kind === "audio" ? (
          <div className="p-4 w-full">
            <audio src={item.url} controls className="w-full" />
          </div>
        ) : item.kind === "model_3d" ? (
          <div className="text-center p-4 space-y-2">
            <span className="text-3xl">📦</span>
            <p className="text-xs text-zinc-400">3D model</p>
            <a
              href={item.url}
              download
              className="inline-block text-xs text-indigo-400 hover:text-indigo-300 underline"
            >
              Download GLB/OBJ
            </a>
          </div>
        ) : (
          <a href={item.url} className="text-xs text-indigo-400 hover:underline p-4 text-center break-all">
            {name}
          </a>
        )}
      </div>
      <div className="p-3 border-t border-white/5">
        <p className="text-xs font-medium truncate">{name}</p>
        <p className="text-xs text-zinc-500 mt-0.5">
          {item.kind} · {formatBytes(item.size_bytes)}
          {subtitle ? ` · ${subtitle}` : ""}
        </p>
      </div>
    </div>
  );
}
