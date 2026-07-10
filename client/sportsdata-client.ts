export type Sport = "football" | "tennis";

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

export interface UpcomingEvent {
  id: number;
  sport: Sport;
  league: string;
  home_participant: string;
  away_participant: string;
  start_time: string;
  status: string;
  prematch_stats?: Record<string, unknown> | null;
  odds?: Array<Record<string, unknown>>;
}

export interface MatchResult {
  id: number;
  sport: Sport;
  league: string;
  home_participant: string;
  away_participant: string;
  start_time: string;
  home_score?: string | null;
  away_score?: string | null;
  source: string;
  stats_payload?: Record<string, unknown>;
  xg_payload?: Record<string, unknown>;
  odds_payload?: Record<string, unknown>;
}

export interface ListResultsParams {
  sport?: Sport;
  league?: string;
  participant?: string;
  source?: string;
  from_date?: string;
  to_date?: string;
  has_stats?: boolean;
  limit?: number;
  offset?: number;
}

export interface ListUpcomingParams {
  sport?: Sport;
  league?: string;
  participant?: string;
  from_date?: string;
  to_date?: string;
  limit?: number;
  offset?: number;
}

export class SportsDataClient {
  constructor(
    private readonly baseUrl: string,
    private readonly apiKey?: string,
  ) {}

  private async request<T>(path: string, init?: RequestInit): Promise<T> {
    const headers = new Headers(init?.headers);
    headers.set("Accept", "application/json");
    if (this.apiKey) {
      headers.set("X-API-Key", this.apiKey);
    }

    const response = await fetch(`${this.baseUrl.replace(/\/$/, "")}${path}`, {
      ...init,
      headers,
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(`SportsData API ${response.status}: ${text}`);
    }

    return response.json() as Promise<T>;
  }

  health(): Promise<Record<string, unknown>> {
    return this.request("/health");
  }

  summary(): Promise<Record<string, unknown>> {
    return this.request("/summary");
  }

  listUpcoming(params: ListUpcomingParams = {}): Promise<PaginatedResponse<UpcomingEvent>> {
    return this.request(`/upcoming${toQuery(params)}`);
  }

  listResults(params: ListResultsParams = {}): Promise<PaginatedResponse<MatchResult>> {
    return this.request(`/results${toQuery(params)}`);
  }

  getResult(id: number): Promise<MatchResult> {
    return this.request(`/results/${id}`);
  }

  getEvent(id: number): Promise<UpcomingEvent> {
    return this.request(`/events/${id}`);
  }

  runJob(jobName: string): Promise<Record<string, unknown>> {
    return this.request(`/jobs/${jobName}`, { method: "POST" });
  }
}

function toQuery(params: Record<string, string | number | boolean | undefined>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null || value === "") {
      continue;
    }
    search.set(key, String(value));
  }
  const query = search.toString();
  return query ? `?${query}` : "";
}
