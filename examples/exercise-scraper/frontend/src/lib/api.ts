import type {
  CorpusBatchJob,
  CorpusRunAllResult,
  CorpusRunInput,
  CorpusRunTopicResult,
  CorpusTopic,
  CreateJobInput,
  DictionaryRunInput,
  DictionaryTrack,
  DriveStatus,
  Exercise,
  Job,
  JobUrl,
  VocabularyExercise,
} from "./types";

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

export async function fetchDriveStatus(): Promise<DriveStatus> {
  return request<DriveStatus>("/api/drive/status");
}

export async function fetchCorpusTopics(): Promise<CorpusTopic[]> {
  const data = await request<{ topics: CorpusTopic[] }>("/api/corpus/topics");
  return data.topics;
}

export async function runCorpusTopic(
  topicId: string,
  input: CorpusRunInput,
): Promise<CorpusRunTopicResult> {
  return request<CorpusRunTopicResult>(`/api/corpus/topics/${topicId}/run`, {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export async function runCorpusAll(
  input: CorpusRunInput,
  limit: number,
): Promise<CorpusRunAllResult> {
  const params = new URLSearchParams({ limit: String(limit) });
  return request<CorpusRunAllResult>(`/api/corpus/run-all?${params.toString()}`, {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export async function fetchJobsByIds(jobIds: string[]): Promise<Job[]> {
  const jobs = await Promise.all(jobIds.map((id) => fetchJob(id)));
  return jobs;
}

export function phaseLabel(phase: string): string {
  const labels: Record<string, string> = {
    queued: "Oczekiwanie w kolejce",
    searching: "Wyszukiwanie w internecie",
    urls_found: "Źródła znalezione",
    crawling: "Pobieranie stron",
    validating: "Walidacja zadań",
    drive_sync: "Synchronizacja z Google Drive",
    completed: "Zbieranie zakończone",
    failed: "Zbieranie nie powiodło się",
  };
  return labels[phase] ?? phase;
}

export function levelLabel(level: string): string {
  return level;
}

export function groupTopicsByLevel(topics: CorpusTopic[]): Record<string, CorpusTopic[]> {
  const grouped: Record<string, CorpusTopic[]> = {};
  for (const topic of topics) {
    grouped[topic.level] = grouped[topic.level] ?? [];
    grouped[topic.level].push(topic);
  }
  const order = ["A1", "A2", "B1", "B2", "C1", "C2"];
  const sorted: Record<string, CorpusTopic[]> = {};
  for (const level of order) {
    if (grouped[level]) sorted[level] = grouped[level];
  }
  for (const level of Object.keys(grouped)) {
    if (!sorted[level]) sorted[level] = grouped[level];
  }
  return sorted;
}

export function groupTopicsByCategory(topics: CorpusTopic[]): Record<string, CorpusTopic[]> {
  const grouped: Record<string, CorpusTopic[]> = { tenses: [], structures: [] };
  for (const topic of topics) {
    const key = topic.category || "structures";
    grouped[key] = grouped[key] ?? [];
    grouped[key].push(topic);
  }
  return grouped;
}

export async function fetchDictionaryTracks(): Promise<DictionaryTrack[]> {
  const data = await request<{ tracks: DictionaryTrack[] }>("/api/dictionary/tracks");
  return data.tracks;
}

export async function runDictionaryTrack(
  trackId: string,
  input: DictionaryRunInput,
): Promise<{ job: Job; track_id: string }> {
  return request<{ job: Job; track_id: string }>(`/api/dictionary/tracks/${trackId}/run`, {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export async function fetchVocabularyExercises(jobId: string): Promise<VocabularyExercise[]> {
  const data = await request<{ exercises: VocabularyExercise[] }>(`/api/jobs/${jobId}/vocabulary`);
  return data.exercises;
}

export type { CorpusBatchJob };
