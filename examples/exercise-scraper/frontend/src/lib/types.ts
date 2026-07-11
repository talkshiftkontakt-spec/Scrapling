export type LangMode = "pl" | "en" | "both";
export type ProviderMode = "duckduckgo" | "serpapi";
export type JobStatus = "queued" | "running" | "completed" | "failed";

export interface Job {
  id: string;
  topic: string;
  lang: LangMode;
  provider: ProviderMode;
  max_pages: number;
  topic_id: string | null;
  status: JobStatus;
  phase: string;
  progress: Record<string, unknown>;
  manifest: Record<string, unknown> | null;
  error: string | null;
  created_at: string;
  updated_at: string;
  finished_at: string | null;
}

export interface Exercise {
  id: string;
  job_id: string;
  text: string;
  topic: string;
  language: string;
  exercise_type: string;
  confidence: number;
  source_url: string;
  source_title: string;
  answers: string | null;
  extracted_at: string;
}

export interface JobUrl {
  url: string;
  title: string;
  query: string;
}

export interface CreateJobInput {
  topic: string;
  lang: LangMode;
  provider: ProviderMode;
  max_pages: number;
  topic_en?: string;
  topic_pl?: string;
  topic_id?: string;
  top_exercises?: number;
  sync_drive?: boolean;
}

export interface CorpusTopic {
  id: string;
  level: string;
  category: string;
  en: string[];
  pl: string[];
  validators: string[];
}

export interface CorpusRunInput {
  lang: LangMode;
  provider: ProviderMode;
  max_pages: number;
  top_exercises: number;
  sync_drive: boolean;
}

export interface CorpusBatchJob {
  job_id: string;
  topic_id: string;
}

export interface CorpusRunTopicResult {
  job: Job;
  topic_id: string;
}

export interface CorpusRunAllResult {
  queued: number;
  jobs: CorpusBatchJob[];
}

export interface DriveStatus {
  configured: boolean;
  package_installed: boolean;
  root_folder_id_set: boolean;
  credentials_available: boolean;
  install_hint: string;
  setup_doc: string;
}

export interface DictionaryTrack {
  id: string;
  level: string;
  language_pair: string[];
  description: string;
  word_count: number;
}

export interface DictionaryRunInput {
  provider: ProviderMode;
  max_pages: number;
  top_exercises: number;
}

export interface VocabularyExercise {
  id: string;
  text: string;
  track_id: string;
  matched_word: string;
  matched_translation: string;
  language: string;
  confidence: number;
  validation_score: number;
  source_url: string;
  extracted_at: string;
}
