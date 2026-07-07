import type { CreateJobInput, Exercise, Job, JobUrl } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed with status ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export async function createJob(input: CreateJobInput): Promise<Job> {
  const data = await request<{ job: Job }>("/api/jobs", {
    method: "POST",
    body: JSON.stringify(input),
  });
  return data.job;
}

export async function fetchJob(jobId: string): Promise<Job> {
  const data = await request<{ job: Job }>(`/api/jobs/${jobId}`);
  return data.job;
}

export async function fetchJobs(): Promise<Job[]> {
  const data = await request<{ jobs: Job[] }>("/api/jobs");
  return data.jobs;
}

export async function fetchExercises(
  jobId: string,
  language: string = "all",
): Promise<{ exercises: Exercise[]; total: number }> {
  const params = new URLSearchParams({ language, limit: "200" });
  return request<{ exercises: Exercise[]; total: number }>(
    `/api/jobs/${jobId}/exercises?${params.toString()}`,
  );
}

export async function fetchJobUrls(jobId: string): Promise<JobUrl[]> {
  const data = await request<{ urls: JobUrl[] }>(`/api/jobs/${jobId}/urls`);
  return data.urls;
}

export function phaseLabel(phase: string): string {
  const labels: Record<string, string> = {
    queued: "Waiting in queue",
    searching: "Searching the web",
    urls_found: "Sources discovered",
    crawling: "Reading pages",
    completed: "Collection finished",
    failed: "Collection failed",
  };
  return labels[phase] ?? phase;
}
