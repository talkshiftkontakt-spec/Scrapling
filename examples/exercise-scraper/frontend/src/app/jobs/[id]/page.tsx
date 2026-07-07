"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import {
  fetchExercises,
  fetchJob,
  fetchJobUrls,
  phaseLabel,
} from "@/lib/api";
import type { Exercise, Job, JobUrl } from "@/lib/types";
import { ApiStatusBanner } from "@/components/api-status-banner";
import { ExerciseList } from "@/components/exercise-list";
import { JobStatusCard } from "@/components/job-status-card";

export default function JobPage() {
  const params = useParams<{ id: string }>();
  const jobId = params.id;
  const [job, setJob] = useState<Job | null>(null);
  const [urls, setUrls] = useState<JobUrl[]>([]);
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [filter, setFilter] = useState("all");
  const [loadingExercises, setLoadingExercises] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!jobId) return;

    let cancelled = false;

    async function load() {
      try {
        const nextJob = await fetchJob(jobId);
        if (cancelled) return;
        setJob(nextJob);
        if (nextJob.status === "completed" || nextJob.phase === "urls_found") {
          const nextUrls = await fetchJobUrls(jobId);
          if (!cancelled) setUrls(nextUrls);
        }
      } catch (loadError) {
        if (!cancelled) {
          setError(loadError instanceof Error ? loadError.message : "Nie udało się wczytać zadania");
        }
      }
    }

    load();
    const timer = window.setInterval(load, 2000);
    return () => {
      cancelled = true;
      window.clearInterval(timer);
    };
  }, [jobId]);

  useEffect(() => {
    if (!jobId || job?.status !== "completed") return;
    setLoadingExercises(true);
    fetchExercises(jobId, filter)
      .then((data) => setExercises(data.exercises))
      .finally(() => setLoadingExercises(false));
  }, [jobId, job?.status, filter]);

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-8 px-6 py-10">
      <div className="flex items-center justify-between gap-4">
        <Link href="/" className="text-sm font-semibold text-[var(--accent)] hover:text-[var(--accent-deep)]">
          Wróć do strony głównej
        </Link>
        {job ? <span className="chip bg-[var(--paper-deep)] text-[var(--ink-soft)]">{phaseLabel(job.phase)}</span> : null}
      </div>

      {error ? (
        <p className="rounded-[1.25rem] bg-[#f6d9d1] px-4 py-3 text-[var(--accent-deep)]">{error}</p>
      ) : null}

      <ApiStatusBanner />

      <JobStatusCard job={job} />

      {urls.length > 0 ? (
        <section className="card-surface rounded-[2rem] p-8">
          <p className="chip bg-[var(--paper-deep)] text-[var(--ink-soft)]">Źródła</p>
          <h3 className="display-title mt-4 text-3xl">Znalezione strony</h3>
          <ul className="mt-6 grid gap-3">
            {urls.map((item) => (
              <li key={item.url} className="rounded-[1.25rem] border border-[var(--line)] bg-[var(--paper)] px-4 py-4">
                <a href={item.url} target="_blank" rel="noreferrer" className="font-medium text-[var(--accent)]">
                  {item.title || item.url}
                </a>
                <p className="mt-1 text-sm text-[var(--ink-soft)]">{item.query}</p>
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      {job?.status === "completed" ? (
        <ExerciseList
          exercises={exercises}
          loading={loadingExercises}
          filter={filter}
          onFilterChange={setFilter}
        />
      ) : null}
    </main>
  );
}
