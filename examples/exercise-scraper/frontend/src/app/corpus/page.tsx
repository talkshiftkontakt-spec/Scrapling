"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import {
  fetchCorpusTopics,
  fetchJob,
  groupTopicsByCategory,
  groupTopicsByLevel,
  runCorpusAll,
  runCorpusTopic,
} from "@/lib/api";
import type { CorpusBatchJob, CorpusRunInput, CorpusTopic, Job } from "@/lib/types";
import { ApiStatusBanner } from "@/components/api-status-banner";
import { DriveStatusBanner } from "@/components/drive-status-banner";
import { CorpusBatchTracker } from "@/components/corpus-batch-tracker";
import { CorpusSettingsPanel } from "@/components/corpus-settings-panel";
import { CorpusTopicGrid } from "@/components/corpus-topic-grid";

const DEFAULT_SETTINGS: CorpusRunInput = {
  lang: "both",
  provider: "duckduckgo",
  max_pages: 10,
  top_exercises: 3,
  sync_drive: false,
};

export default function CorpusPage() {
  const router = useRouter();
  const [category, setCategory] = useState<"tenses" | "structures">("tenses");
  const [topics, setTopics] = useState<CorpusTopic[]>([]);
  const [settings, setSettings] = useState<CorpusRunInput>(DEFAULT_SETTINGS);
  const [batchLimit, setBatchLimit] = useState(5);
  const [loadingTopics, setLoadingTopics] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [runningTopicId, setRunningTopicId] = useState<string | null>(null);
  const [runningBatch, setRunningBatch] = useState(false);
  const [batchJobs, setBatchJobs] = useState<CorpusBatchJob[]>([]);
  const [topicJobs, setTopicJobs] = useState<Record<string, Job>>({});
  const [batchJobMap, setBatchJobMap] = useState<Record<string, Job>>({});

  const grouped = useMemo(() => {
    const filtered = topics.filter((topic) => topic.category === category);
    return groupTopicsByLevel(filtered);
  }, [topics, category]);
  const topicNames = useMemo(() => {
    const map: Record<string, string> = {};
    for (const topic of topics) {
      map[topic.id] = topic.en[0] ?? topic.id;
    }
    return map;
  }, [topics]);

  useEffect(() => {
    fetchCorpusTopics()
      .then(setTopics)
      .catch((loadError) => {
        setError(loadError instanceof Error ? loadError.message : "Nie udało się wczytać taksonomii");
      })
      .finally(() => setLoadingTopics(false));
  }, []);

  const pollJobIds = useCallback(async (jobIds: string[]) => {
    if (jobIds.length === 0) return;
    const results = await Promise.all(
      jobIds.map(async (jobId) => {
        try {
          return await fetchJob(jobId);
        } catch {
          return null;
        }
      }),
    );
    const byId: Record<string, Job> = {};
    for (const job of results) {
      if (job) byId[job.id] = job;
    }
    setBatchJobMap((prev) => ({ ...prev, ...byId }));

    setTopicJobs((prev) => {
      const next = { ...prev };
      for (const job of results) {
        if (job?.topic_id) next[job.topic_id] = job;
      }
      return next;
    });
  }, []);

  useEffect(() => {
    const jobIds = batchJobs.map((item) => item.job_id);
    if (jobIds.length === 0) return;

    pollJobIds(jobIds).catch(() => undefined);
    const timer = window.setInterval(() => {
      pollJobIds(jobIds).catch(() => undefined);
    }, 2000);
    return () => window.clearInterval(timer);
  }, [batchJobs, pollJobIds]);

  async function handleRunTopic(topicId: string) {
    setRunningTopicId(topicId);
    setError(null);
    try {
      const result = await runCorpusTopic(topicId, settings);
      setTopicJobs((prev) => ({ ...prev, [topicId]: result.job }));
      router.push(`/jobs/${result.job.id}`);
    } catch (runError) {
      setError(runError instanceof Error ? runError.message : "Nie udało się uruchomić tematu");
    } finally {
      setRunningTopicId(null);
    }
  }

  async function handleRunAll() {
    setRunningBatch(true);
    setError(null);
    try {
      const result = await runCorpusAll(settings, batchLimit);
      setBatchJobs(result.jobs);
      const initial: Record<string, Job> = {};
      await Promise.all(
        result.jobs.map(async (item) => {
          const job = await fetchJob(item.job_id);
          initial[item.job_id] = job;
          if (job.topic_id) {
            setTopicJobs((prev) => ({ ...prev, [job.topic_id as string]: job }));
          }
        }),
      );
      setBatchJobMap(initial);
    } catch (runError) {
      setError(runError instanceof Error ? runError.message : "Nie udało się uruchomić batcha");
    } finally {
      setRunningBatch(false);
    }
  }

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-8 px-6 py-8">
        <header className="animate-rise">
          <p className="chip bg-[var(--sage-soft)] text-[var(--sage)]">Grammar Corpus</p>
          <h1 className="display-title mt-5 max-w-3xl text-5xl leading-tight text-[var(--ink)] sm:text-6xl">
            Czasy i struktury — 20 tematów z walidatorami
          </h1>
          <p className="mt-5 max-w-2xl text-lg leading-8 text-[var(--ink-soft)]">
            Wybierz temat gramatyczny: <strong>czasy</strong> (8) lub <strong>struktury</strong> (12).
            Każdy temat zapisuje ćwiczenia do{" "}
            <code className="rounded bg-[var(--paper-deep)] px-2 py-0.5 text-sm">grammar-corpus/grammar/</code>.
            Słownictwo jest w zakładce{" "}
            <a href="/dictionary" className="font-semibold text-[var(--accent)]">Słówka</a>.
          </p>
          <div className="mt-6 flex flex-wrap gap-2">
            {(["tenses", "structures"] as const).map((key) => (
              <button
                key={key}
                type="button"
                onClick={() => setCategory(key)}
                className={`rounded-full px-5 py-2.5 text-sm font-semibold transition ${
                  category === key
                    ? "bg-[var(--accent)] text-white"
                    : "bg-[var(--card)] text-[var(--ink-soft)] ring-1 ring-[var(--line)]"
                }`}
              >
                {key === "tenses" ? "Czasy" : "Struktury"}
              </button>
            ))}
          </div>
        </header>

        {error ? (
          <p className="rounded-[1.25rem] bg-[#f6d9d1] px-4 py-3 text-[var(--accent-deep)]">{error}</p>
        ) : null}

        <ApiStatusBanner />
        <DriveStatusBanner />

        <CorpusSettingsPanel
          settings={settings}
          batchLimit={batchLimit}
          onChange={setSettings}
          onBatchLimitChange={setBatchLimit}
          onRunAll={handleRunAll}
          runningBatch={runningBatch}
        />

        <CorpusBatchTracker
          batchJobs={batchJobs}
          jobs={batchJobMap}
          topicNames={topicNames}
        />

        {loadingTopics ? (
          <p className="text-[var(--ink-soft)]">Ładuję taksonomię gramatyczną...</p>
        ) : (
          <CorpusTopicGrid
            grouped={grouped}
            runningTopicId={runningTopicId}
            topicJobs={topicJobs}
            onRunTopic={handleRunTopic}
          />
        )}
      </main>
  );
}
