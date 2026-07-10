"use client";

import Link from "next/link";
import type { CorpusTopic } from "@/lib/types";
import { phaseLabel } from "@/lib/api";
import type { Job } from "@/lib/types";

interface CorpusTopicGridProps {
  grouped: Record<string, CorpusTopic[]>;
  runningTopicId: string | null;
  topicJobs: Record<string, Job | undefined>;
  onRunTopic: (topicId: string) => void;
}

function statusChip(status: Job["status"] | undefined) {
  if (!status) return null;
  const tones: Record<Job["status"], string> = {
    completed: "bg-[var(--sage-soft)] text-[var(--sage)]",
    failed: "bg-[#f6d9d1] text-[var(--accent-deep)]",
    running: "bg-[#f8e7cf] text-[#9a6a1d]",
    queued: "bg-[var(--paper-deep)] text-[var(--ink-soft)]",
  };
  return <span className={`chip ${tones[status]}`}>{status}</span>;
}

export function CorpusTopicGrid({
  grouped,
  runningTopicId,
  topicJobs,
  onRunTopic,
}: CorpusTopicGridProps) {
  return (
    <div className="grid gap-8">
      {Object.entries(grouped).map(([level, topics]) => (
        <section key={level} className="card-surface rounded-[2rem] p-8">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="chip bg-[var(--sage-soft)] text-[var(--sage)]">Poziom {level}</p>
              <h3 className="display-title mt-3 text-3xl">{topics.length} tematów</h3>
            </div>
          </div>

          <ul className="mt-6 grid gap-4 lg:grid-cols-2">
            {topics.map((topic) => {
              const job = topicJobs[topic.id];
              const isRunning = runningTopicId === topic.id;
              return (
                <li
                  key={topic.id}
                  className="rounded-[1.5rem] border border-[var(--line)] bg-[var(--paper)] p-5"
                >
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--ink-soft)]">
                        {topic.id}
                      </p>
                      <h4 className="display-title mt-1 text-2xl text-[var(--ink)]">{topic.en[0]}</h4>
                      <p className="mt-1 text-sm text-[var(--ink-soft)]">{topic.pl[0]}</p>
                    </div>
                    {statusChip(job?.status)}
                  </div>

                  <div className="mt-3 flex flex-wrap gap-2">
                    {topic.validators.map((validator) => (
                      <span key={validator} className="chip bg-white text-[var(--ink-soft)] ring-1 ring-[var(--line)]">
                        {validator}
                      </span>
                    ))}
                  </div>

                  {job ? (
                    <p className="mt-4 text-sm text-[var(--ink-soft)]">
                      {phaseLabel(job.phase)}
                      {job.status === "completed" ? (
                        <> · top {String(job.progress?.top_exercises ?? job.progress?.exercises_total ?? "—")}</>
                      ) : null}
                    </p>
                  ) : null}

                  <div className="mt-5 flex flex-wrap gap-3">
                    <button
                      type="button"
                      onClick={() => onRunTopic(topic.id)}
                      disabled={isRunning || job?.status === "running" || job?.status === "queued"}
                      className="rounded-full bg-[var(--accent)] px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-[var(--accent-deep)] disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      {isRunning ? "Uruchamiam..." : "Zbierz temat"}
                    </button>
                    {job ? (
                      <Link
                        href={`/jobs/${job.id}`}
                        className="rounded-full bg-white px-5 py-2.5 text-sm font-semibold text-[var(--accent)] ring-1 ring-[var(--line)] transition hover:bg-[var(--card)]"
                      >
                        Szczegóły zadania
                      </Link>
                    ) : null}
                  </div>
                </li>
              );
            })}
          </ul>
        </section>
      ))}
    </div>
  );
}
