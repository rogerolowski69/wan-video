type StatusBadgeProps = {
  status: string;
};

const STYLES: Record<string, string> = {
  completed: "bg-emerald-500/15 text-emerald-300 ring-emerald-500/30",
  running: "bg-amber-500/15 text-amber-300 ring-amber-500/30",
  failed: "bg-red-500/15 text-red-300 ring-red-500/30",
  pending: "bg-zinc-500/15 text-zinc-300 ring-zinc-500/30",
};

export function StatusBadge({ status }: StatusBadgeProps): React.JSX.Element {
  const style = STYLES[status] ?? STYLES.pending;
  return (
    <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium ring-1 ring-inset ${style}`}>
      {status}
    </span>
  );
}
