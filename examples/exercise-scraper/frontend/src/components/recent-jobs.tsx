import Link from "next/link";
import type { Job } from "@/lib/types";

interface RecentJobsProps {
  jobs: Job[];
}

export function RecentJobs({ jobs }: RecentJobsProps) {
  if (jobs.length === 0) {
    return null;
  }

  return (
    <section className="card-surface rounded-[2rem] p-8">
      <p className="chip bg-[var(--paper-deep)] text-[var(--ink-soft)]">Historia</p>
      <h3 className="display-title mt-4 text-3xl">Ostatnie zbierania</h3>
      <ul className="mt-6 grid gap-3">
        {jobs.map((job) => (
          <li key={job.id}>
            <Link
              href={`/jobs/${job.id}`}
              className="flex flex-wrap items-center justify-between gap-3 rounded-[1.25rem] border border-[var(--line)] bg-[var(--paper)] px-4 py-4 transition hover:border-[var(--accent)]"
            >
              <div>
                <p className="font-semibold text-[var(--ink)]">{job.topic}</p>
                <p className="text-sm text-[var(--ink-soft)]">{job.lang} · {job.status}</p>
              </div>
              <span className="text-sm text-[var(--ink-soft)]">
                {new Date(job.created_at).toLocaleString("pl-PL")}
              </span>
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}
