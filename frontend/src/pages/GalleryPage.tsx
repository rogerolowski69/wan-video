import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getGallery, type GalleryItem } from "../api";
import { MediaTile } from "../components/MediaTile";

export function GalleryPage(): React.JSX.Element {
  const [items, setItems] = useState<GalleryItem[]>([]);
  const [filter, setFilter] = useState<string>("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    async function load(): Promise<void> {
      try {
        const data = await getGallery(120);
        if (!cancelled) setItems(data);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    void load();
  }, []);

  const kinds = ["all", ...new Set(items.map((i) => i.kind))];
  const filtered = filter === "all" ? items : items.filter((i) => i.kind === filter);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Gallery</h1>
        <p className="text-zinc-400 text-sm mt-1">All media stored in MinIO</p>
      </div>

      <div className="flex flex-wrap gap-2">
        {kinds.map((kind) => (
          <button
            key={kind}
            type="button"
            onClick={() => setFilter(kind)}
            className={`px-3 py-1 rounded-full text-xs capitalize transition-colors ${
              filter === kind
                ? "bg-indigo-500/25 text-indigo-200"
                : "bg-white/5 text-zinc-400 hover:text-zinc-200"
            }`}
          >
            {kind}
          </button>
        ))}
      </div>

      {loading ? (
        <p className="text-zinc-500 text-sm">Loading gallery…</p>
      ) : filtered.length === 0 ? (
        <p className="text-zinc-500 text-sm">No media artifacts yet.</p>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          {filtered.map((item) => (
            <div key={item.id} className="relative group">
              <MediaTile item={item} subtitle={`run #${item.run_id}`} />
              <Link
                to={`/runs/${item.run_id}`}
                className="absolute inset-0 rounded-xl ring-2 ring-transparent group-hover:ring-indigo-500/40 transition-all"
                aria-label={`View run ${item.run_id}`}
              />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
