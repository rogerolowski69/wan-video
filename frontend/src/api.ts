export type Artifact = {
  path: string;
  kind: string;
  size_bytes: number | null;
  url: string;
};

export type Run = {
  id: number;
  script: string;
  model: string;
  backend: string;
  provider: string | null;
  status: string;
  error: string | null;
  prompt: string | null;
  started_at: string;
  completed_at: string | null;
  artifacts: Artifact[];
};

export type GalleryItem = {
  id: number;
  run_id: number;
  path: string;
  kind: string;
  size_bytes: number | null;
  url: string;
  created_at: string;
};

export type Health = {
  status: string;
  storage: string;
  missing_env?: string;
};

export type ScriptsResponse = {
  scripts: string[];
  by_modality: Record<string, string[]>;
  labels: Record<string, string>;
};

const API_BASE = import.meta.env.VITE_API_URL ?? "/api";

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`);
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`);
  }
  return response.json() as Promise<T>;
}

export function getHealth(): Promise<Health> {
  return fetchJson<Health>("/health");
}

export function getRuns(limit = 50): Promise<Run[]> {
  return fetchJson<Run[]>(`/runs?limit=${limit}`);
}

export function getRun(id: number): Promise<Run> {
  return fetchJson<Run>(`/runs/${id}`);
}

export function getGallery(limit = 100): Promise<GalleryItem[]> {
  return fetchJson<GalleryItem[]>(`/gallery?limit=${limit}`);
}

export function getScripts(): Promise<ScriptsResponse> {
  return fetchJson<ScriptsResponse>("/scripts");
}

export function resolveMediaUrl(url: string): string {
  if (url.startsWith("http")) {
    return url;
  }
  if (url.startsWith("/api/")) {
    return url;
  }
  return `${API_BASE}${url.replace(/^\/api/, "")}`;
}

export function formatBytes(bytes: number | null): string {
  if (bytes == null) return "—";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function scriptLabel(script: string, labels?: Record<string, string>): string {
  return labels?.[script] ?? script.split("/").pop()?.replace(/_/g, " ") ?? script;
}

export function formatDate(iso: string): string {
  return new Date(iso).toLocaleString();
}
