"use client";

import Link from "next/link";
import type { CorpusBatchJob, Job } from "@/lib/types";
import { phaseLabel } from "@/lib/api";

interface CorpusBatchTrackerProps {
  batchJobs: CorpusBatchJob[];
  jobs: Record<string, Job | undefined>;
  topicNames: Record<string, string>;
}

export function CorpusBatchTracker({ batchJobs, jobs, topicNames }: CorpusBatchTrackerProps) {
  if (batchJobs.length === 0) return null;

  const completed = batchJobs.filter((item) => jobs[item.job_id]?.status === "completed").length;
  const failed = batchJobs.filter((item) => jobs[item.job_id]?.status === "failed").length;
  const running = batchJobs.filter((item) => {
    const status = jobs[item.job_id]?.status;
    return status === "running" || status === "queued";
  }).length;

  return (
    <section className="card-surface rounded-[2rem] p-8">
      <p className="chip bg-[var(--paper-deep)] text-[var(--ink-soft)]">Batch w toku</p>
      <h3 className="display-title mt-4 text-3xl">Postęp zbiorczego zbierania</h3>
      <p className="mt-2 text-[var(--ink-soft)]">
        {completed} ukończone · {running} w toku · {failed} błędy · {batchJobs.length} łącznie
      </p>

      <ul className="mt-6 grid max-h-80 gap-2 overflow-y-auto pr-1">
        {batchJobs.map((item) => {
          const job = jobs[item.job_id];
          const title = topicNames[item.topic_id] ?? item.topic_id;
          return (
            <li
              key={item.job_id}
              className="flex flex-wrap items-center justify-between gap-3 rounded-[1rem] border border-[var(--line)] bg-[var(--paper)] px-4 py-3"
            >
              <div>
                <p className="font-medium text-[var(--ink)]">{title}</p>
                <p className="text-sm text-[var(--ink-soft)]">
                  {job ? phaseLabel(job.phase) : "Ładowanie..."}
                </p>
              </div>
              <div className="flex items-center gap-2">
                {job ? (
                  <span className="chip bg-white text-[var(--ink-soft)] ring-1 ring-[var(--line)]">
                    {job.status}
                  </span>
                ) : null}
                <Link
                  href={`/jobs/${item.job_id}`}
                  className="text-sm font-semibold text-[var(--accent)] hover:text-[var(--accent-deep)]"
                >
                  Otwórz
                </Link>
              </div>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
