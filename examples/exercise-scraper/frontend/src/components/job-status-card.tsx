import type { Job } from "@/lib/types";
import { phaseLabel } from "@/lib/api";

interface JobStatusProps {
  job: Job | null;
}

function statusTone(status: Job["status"]) {
  if (status === "completed") return "bg-[var(--sage-soft)] text-[var(--sage)]";
  if (status === "failed") return "bg-[#f6d9d1] text-[var(--accent-deep)]";
  if (status === "running") return "bg-[#f8e7cf] text-[#9a6a1d]";
  return "bg-[var(--paper-deep)] text-[var(--ink-soft)]";
}

export function JobStatusCard({ job }: JobStatusProps) {
  if (!job) {
    return (
      <div className="card-surface rounded-[2rem] p-8 text-[var(--ink-soft)]">
        Uruchom zbieranie, aby zobaczyć postęp i wyniki.
      </div>
    );
  }

  const progress = job.progress ?? {};
  const total = Number(progress.exercises_total ?? 0);
  const pl = Number(progress.exercises_pl ?? 0);
  const en = Number(progress.exercises_en ?? 0);
  const passed = progress.passed != null ? Number(progress.passed) : null;
  const rejected = progress.rejected != null ? Number(progress.rejected) : null;
  const topN = progress.top_exercises != null ? Number(progress.top_exercises) : null;

  return (
    <div className="card-surface animate-rise rounded-[2rem] p-8">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="chip bg-[var(--paper-deep)] text-[var(--ink-soft)]">Aktywne zadanie</p>
          <h3 className="display-title mt-4 text-3xl">{job.topic}</h3>
          {job.topic_id ? (
            <p className="mt-2 text-sm text-[var(--ink-soft)]">
              Korpus: <span className="font-medium text-[var(--ink)]">{job.topic_id}</span>
            </p>
          ) : null}
        </div>
        <span className={`chip ${statusTone(job.status)}`}>{job.status}</span>
      </div>

      <div className="mt-6 rounded-[1.5rem] bg-[var(--paper)] p-5">
        <p className="text-sm font-semibold uppercase tracking-[0.18em] text-[var(--ink-soft)]">
          Etap
        </p>
        <p className="mt-2 text-xl font-medium text-[var(--ink)]">{phaseLabel(job.phase)}</p>
        {job.status === "running" ? (
          <div className="progress-glow mt-4 h-2 overflow-hidden rounded-full bg-[var(--line)]">
            <div className="h-full w-2/3 rounded-full bg-[var(--accent)]" />
          </div>
        ) : null}
      </div>

      {job.status === "failed" && job.error ? (
        <p className="mt-5 rounded-2xl bg-[#f6d9d1] px-4 py-3 text-[var(--accent-deep)]">{job.error}</p>
      ) : null}

      {job.status === "completed" ? (
        <dl className="mt-6 grid gap-4 sm:grid-cols-3">
          <div className="rounded-[1.25rem] bg-[var(--paper)] p-4">
            <dt className="text-sm text-[var(--ink-soft)]">Zapisane (top N)</dt>
            <dd className="display-title mt-2 text-3xl">{total}</dd>
          </div>
          <div className="rounded-[1.25rem] bg-[var(--paper)] p-4">
            <dt className="text-sm text-[var(--ink-soft)]">Polski</dt>
            <dd className="display-title mt-2 text-3xl">{pl}</dd>
          </div>
          <div className="rounded-[1.25rem] bg-[var(--paper)] p-4">
            <dt className="text-sm text-[var(--ink-soft)]">Angielski</dt>
            <dd className="display-title mt-2 text-3xl">{en}</dd>
          </div>
          {passed != null ? (
            <div className="rounded-[1.25rem] bg-[var(--paper)] p-4 sm:col-span-3">
              <dt className="text-sm text-[var(--ink-soft)]">Walidacja</dt>
              <dd className="mt-2 text-base text-[var(--ink)]">
                {passed} przeszło · {rejected ?? 0} odrzucono
                {topN != null ? ` · top ${topN} zapisano` : null}
              </dd>
            </div>
          ) : null}
        </dl>
      ) : null}
    </div>
  );
}
