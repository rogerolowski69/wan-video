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

export type GenerationModelInfo = {
  id: string;
  path: string;
  label: string;
  modality: string;
  modality_label: string;
  model_id: string;
  backend: string;
  description: string;
  emoji: string;
  just_recipe: string;
};

export type CatalogResponse = {
  scripts: string[];
  by_modality: Record<string, string[]>;
  labels: Record<string, string>;
  modality_labels: Record<string, string>;
  models: GenerationModelInfo[];
};

export type Job = {
  job_id: string;
  model_id: string;
  script: string;
  demo: boolean;
  status: string;
  started_at: string;
  exit_code: number | null;
  error: string | null;
};

import type { AuthConfig, AuthResponse, AuthUser, MeResponse } from "./auth";
import { authHeaders, setAuthToken } from "./auth";

const API_BASE = import.meta.env.VITE_API_URL ?? "/api";

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers);
  if (!headers.has("Content-Type") && init?.body) {
    headers.set("Content-Type", "application/json");
  }
  for (const [key, value] of Object.entries(authHeaders())) {
    headers.set(key, value);
  }
  const response = await fetch(`${API_BASE}${path}`, { ...init, headers });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `${response.status} ${response.statusText}`);
  }
  return response.json() as Promise<T>;
}

export function getHealth(): Promise<Health> {
  return fetchJson<Health>("/health");
}

export function getCatalog(): Promise<CatalogResponse> {
  return fetchJson<CatalogResponse>("/catalog");
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

export function getJob(jobId: string): Promise<Job> {
  return fetchJson<Job>(`/jobs/${jobId}`);
}

export function launchModel(
  modelId: string,
  options: { demo?: boolean; provider?: string } = {},
): Promise<Job> {
  return fetchJson<Job>(`/generate/${modelId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      demo: options.demo ?? true,
      provider: options.provider ?? null,
    }),
  });
}

export function launchRunAll(continueOnError = true): Promise<Job> {
  return fetchJson<Job>("/generate/run-all", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ continue_on_error: continueOnError }),
  });
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

export function getAuthConfig(): Promise<AuthConfig> {
  return fetchJson<AuthConfig>("/auth/config");
}

export function getMe(): Promise<MeResponse> {
  return fetchJson<MeResponse>("/auth/me");
}

export function loginTelegram(initData: string): Promise<AuthResponse> {
  return fetchJson<AuthResponse>("/auth/telegram", {
    method: "POST",
    body: JSON.stringify({ init_data: initData }),
  });
}

export function loginTon(walletAddress: string): Promise<AuthResponse> {
  return fetchJson<AuthResponse>("/auth/ton", {
    method: "POST",
    body: JSON.stringify({ wallet_address: walletAddress }),
  });
}

export function logout(): void {
  setAuthToken(null);
}

export type { AuthUser };
