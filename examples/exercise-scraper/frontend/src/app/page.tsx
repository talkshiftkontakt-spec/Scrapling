"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  createJob,
  fetchExercises,
  fetchJob,
  fetchJobs,
} from "@/lib/api";
import type { CreateJobInput, Exercise, Job } from "@/lib/types";
import { ApiStatusBanner } from "@/components/api-status-banner";
import { ExerciseList } from "@/components/exercise-list";
import { JobStatusCard } from "@/components/job-status-card";
import { RecentJobs } from "@/components/recent-jobs";
import { SearchPanel } from "@/components/search-panel";

export default function HomePage() {
  const router = useRouter();
  const [submitting, setSubmitting] = useState(false);
  const [activeJob, setActiveJob] = useState<Job | null>(null);
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [exerciseTotal, setExerciseTotal] = useState(0);
  const [filter, setFilter] = useState("all");
  const [loadingExercises, setLoadingExercises] = useState(false);
  const [recentJobs, setRecentJobs] = useState<Job[]>([]);
  const [error, setError] = useState<string | null>(null);

  const refreshRecent = useCallback(async () => {
    const jobs = await fetchJobs();
    setRecentJobs(jobs.filter((job) => job.id !== activeJob?.id).slice(0, 5));
  }, [activeJob?.id]);

  useEffect(() => {
    refreshRecent().catch(() => undefined);
  }, [refreshRecent]);

  useEffect(() => {
    if (!activeJob) return;
    if (activeJob.status !== "running" && activeJob.status !== "queued") return;

    const timer = window.setInterval(async () => {
      const job = await fetchJob(activeJob.id);
      setActiveJob(job);
      if (job.status === "completed" || job.status === "failed") {
        window.clearInterval(timer);
      }
    }, 2000);

    return () => window.clearInterval(timer);
  }, [activeJob]);

  useEffect(() => {
    if (!activeJob || activeJob.status !== "completed") {
      setExercises([]);
      setExerciseTotal(0);
      return;
    }

    setLoadingExercises(true);
    fetchExercises(activeJob.id, filter)
      .then((data) => {
        setExercises(data.exercises);
        setExerciseTotal(data.total);
      })
      .finally(() => setLoadingExercises(false));
  }, [activeJob, filter]);

  async function handleSubmit(input: CreateJobInput) {
    setSubmitting(true);
    setError(null);
    try {
      const job = await createJob(input);
      setActiveJob(job);
      router.push(`/jobs/${job.id}`);
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Nie udało się uruchomić zadania");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-8 px-6 py-10">
      <header className="animate-rise">
        <p className="chip bg-[#f8e7cf] text-[#9a6a1d]">Exercise Scraper</p>
        <h1 className="display-title mt-5 max-w-3xl text-5xl leading-tight text-[var(--ink)] sm:text-6xl">
          Zbieraj ćwiczenia z całego internetu w jednym miejscu
        </h1>
        <p className="mt-5 max-w-2xl text-lg leading-8 text-[var(--ink-soft)]">
          Wpisz temat gramatyki, wybierz język źródeł i pobierz gotowe zadania zapisane w bazie oraz w plikach JSON.
        </p>
      </header>

      {error ? (
        <p className="rounded-[1.25rem] bg-[#f6d9d1] px-4 py-3 text-[var(--accent-deep)]">{error}</p>
      ) : null}

      <ApiStatusBanner />

      <div className="grid gap-8 lg:grid-cols-[1.15fr_0.85fr]">
        <SearchPanel loading={submitting} onSubmit={handleSubmit} />
        <JobStatusCard job={activeJob} />
      </div>

      {activeJob?.status === "completed" ? (
        <ExerciseList
          exercises={exercises}
          loading={loadingExercises}
          filter={filter}
          onFilterChange={setFilter}
        />
      ) : null}

      {activeJob?.status === "completed" ? (
        <p className="text-sm text-[var(--ink-soft)]">Łącznie zapisano {exerciseTotal} zadań.</p>
      ) : null}

      <RecentJobs jobs={recentJobs} />
    </main>
  );
}
