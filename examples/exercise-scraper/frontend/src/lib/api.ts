import type { CreateJobInput, Exercise, Job, JobUrl } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(init?.headers ?? {}),
      },
      cache: "no-store",
    });
  } catch {
    throw new Error(
      "Brak połączenia z API. Uruchom backend: ./examples/exercise-scraper/scripts/run-api.sh",
    );
  }

  if (!response.ok) {
    let detail = await response.text();
    try {
      const parsed = JSON.parse(detail) as { detail?: string };
      if (parsed.detail) detail = parsed.detail;
    } catch {
      // keep raw text
    }
    throw new Error(detail || `Błąd serwera: ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export async function checkApiHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE}/api/health`, { cache: "no-store" });
    return response.ok;
  } catch {
    return false;
  }
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
    queued: "Oczekiwanie w kolejce",
    searching: "Wyszukiwanie w internecie",
    urls_found: "Źródła znalezione",
    crawling: "Pobieranie stron",
    completed: "Zbieranie zakończone",
    failed: "Zbieranie nie powiodło się",
  };
  return labels[phase] ?? phase;
}
