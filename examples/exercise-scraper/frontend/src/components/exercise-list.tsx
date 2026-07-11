import type { Exercise } from "@/lib/types";

interface ExerciseListProps {
  exercises: Exercise[];
  loading: boolean;
  filter: string;
  onFilterChange: (value: string) => void;
}

function languageLabel(language: string) {
  if (language === "pl") return "PL";
  if (language === "en") return "EN";
  return "?";
}

export function ExerciseList({
  exercises,
  loading,
  filter,
  onFilterChange,
}: ExerciseListProps) {
  return (
    <section className="card-surface rounded-[2rem] p-8">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="chip bg-[var(--sage-soft)] text-[var(--sage)]">Wyniki</p>
          <h3 className="display-title mt-4 text-3xl">Zebrane zadania</h3>
        </div>
        <select
          value={filter}
          onChange={(event) => onFilterChange(event.target.value)}
          className="rounded-full border border-[var(--line)] bg-white px-4 py-2 text-sm outline-none ring-[var(--accent)] focus:ring-2"
        >
          <option value="all">Wszystkie języki</option>
          <option value="pl">Polski</option>
          <option value="en">Angielski</option>
          <option value="unknown">Nieznany</option>
        </select>
      </div>

      {loading ? (
        <p className="mt-8 text-[var(--ink-soft)]">Ładuję zadania...</p>
      ) : exercises.length === 0 ? (
        <p className="mt-8 text-[var(--ink-soft)]">
          Jeszcze nie ma zadań. Poczekaj aż zbieranie się zakończy.
        </p>
      ) : (
        <ul className="mt-8 grid gap-4">
          {exercises.map((exercise, index) => (
            <li
              key={exercise.id}
              className="animate-rise rounded-[1.5rem] border border-[var(--line)] bg-[var(--paper)] p-5"
              style={{ animationDelay: `${index * 40}ms` }}
            >
              <div className="flex flex-wrap items-center gap-3">
                <span className="chip bg-white text-[var(--ink-soft)]">
                  {languageLabel(exercise.language)}
                </span>
                <span className="chip bg-white text-[var(--ink-soft)]">
                  {Math.round(exercise.confidence * 100)}%
                </span>
                <span className="chip bg-white text-[var(--ink-soft)]">{exercise.exercise_type}</span>
              </div>
              <p className="mt-4 text-lg leading-8 text-[var(--ink)]">{exercise.text}</p>
              <a
                href={exercise.source_url}
                target="_blank"
                rel="noreferrer"
                className="mt-4 inline-block text-sm font-medium text-[var(--accent)] hover:text-[var(--accent-deep)]"
              >
                {exercise.source_title || exercise.source_url}
              </a>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
