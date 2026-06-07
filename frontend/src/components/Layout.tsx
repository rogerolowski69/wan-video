import { Link, Outlet, useLocation } from "react-router-dom";

const NAV = [
  { to: "/", label: "Studio" },
  { to: "/runs", label: "Runs" },
  { to: "/gallery", label: "Gallery" },
] as const;

export function Layout(): React.JSX.Element {
  const location = useLocation();

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-white/10 bg-black/40 backdrop-blur-md sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between gap-4">
          <Link to="/" className="flex items-center gap-2 font-semibold text-lg tracking-tight">
            <span className="text-2xl" aria-hidden>
              🎬
            </span>
            wan-video
          </Link>
          <nav className="flex gap-1">
            {NAV.map((item) => {
              const active =
                item.to === "/"
                  ? location.pathname === "/"
                  : location.pathname.startsWith(item.to);
              return (
                <Link
                  key={item.to}
                  to={item.to}
                  className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${
                    active
                      ? "bg-indigo-500/20 text-indigo-200"
                      : "text-zinc-400 hover:text-zinc-100 hover:bg-white/5"
                  }`}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>
      </header>
      <main className="flex-1 max-w-6xl w-full mx-auto px-4 py-8">
        <Outlet />
      </main>
      <footer className="border-t border-white/5 py-4 text-center text-xs text-zinc-500">
        fal.ai + Hugging Face inference · outputs in MinIO
      </footer>
    </div>
  );
}
