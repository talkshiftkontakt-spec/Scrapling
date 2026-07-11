"use client";

import type { CorpusRunInput, LangMode, ProviderMode } from "@/lib/types";

interface CorpusSettingsPanelProps {
  settings: CorpusRunInput;
  batchLimit: number;
  onChange: (settings: CorpusRunInput) => void;
  onBatchLimitChange: (limit: number) => void;
  onRunAll: () => void;
  runningBatch: boolean;
}

export function CorpusSettingsPanel({
  settings,
  batchLimit,
  onChange,
  onBatchLimitChange,
  onRunAll,
  runningBatch,
}: CorpusSettingsPanelProps) {
  function update<K extends keyof CorpusRunInput>(key: K, value: CorpusRunInput[K]) {
    onChange({ ...settings, [key]: value });
  }

  return (
    <section className="card-surface animate-rise rounded-[2rem] p-8">
      <p className="chip bg-[#f8e7cf] text-[#9a6a1d]">Ustawienia korpusu</p>
      <h2 className="display-title mt-4 text-3xl text-[var(--ink)]">Parametry zbierania</h2>
      <p className="mt-3 max-w-2xl text-base leading-7 text-[var(--ink-soft)]">
        Te ustawienia dotyczą pojedynczego tematu i zbiorczego uruchomienia wielu klas gramatycznych.
      </p>

      <div className="mt-6 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
        <label className="grid gap-2">
          <span className="text-sm font-semibold uppercase tracking-[0.18em] text-[var(--ink-soft)]">
            Język źródeł
          </span>
          <select
            value={settings.lang}
            onChange={(event) => update("lang", event.target.value as LangMode)}
            className="rounded-2xl border border-[var(--line)] bg-white px-4 py-3 outline-none ring-[var(--accent)] transition focus:ring-2"
          >
            <option value="both">Polski i angielski</option>
            <option value="pl">Tylko polski</option>
            <option value="en">Tylko angielski</option>
          </select>
        </label>

        <label className="grid gap-2">
          <span className="text-sm font-semibold uppercase tracking-[0.18em] text-[var(--ink-soft)]">
            Wyszukiwarka
          </span>
          <select
            value={settings.provider}
            onChange={(event) => update("provider", event.target.value as ProviderMode)}
            className="rounded-2xl border border-[var(--line)] bg-white px-4 py-3 outline-none ring-[var(--accent)] transition focus:ring-2"
          >
            <option value="duckduckgo">DuckDuckGo</option>
            <option value="serpapi">SerpAPI</option>
          </select>
        </label>

        <label className="grid gap-2">
          <span className="text-sm font-semibold uppercase tracking-[0.18em] text-[var(--ink-soft)]">
            Limit stron / temat
          </span>
          <input
            type="number"
            min={1}
            max={60}
            value={settings.max_pages}
            onChange={(event) => update("max_pages", Number(event.target.value))}
            className="rounded-2xl border border-[var(--line)] bg-white px-4 py-3 outline-none ring-[var(--accent)] transition focus:ring-2"
          />
        </label>

        <label className="grid gap-2">
          <span className="text-sm font-semibold uppercase tracking-[0.18em] text-[var(--ink-soft)]">
            Top N zadań
          </span>
          <input
            type="number"
            min={1}
            max={100}
            value={settings.top_exercises}
            onChange={(event) => update("top_exercises", Number(event.target.value))}
            className="rounded-2xl border border-[var(--line)] bg-white px-4 py-3 outline-none ring-[var(--accent)] transition focus:ring-2"
          />
        </label>

        <label className="grid gap-2">
          <span className="text-sm font-semibold uppercase tracking-[0.18em] text-[var(--ink-soft)]">
            Limit tematów (batch)
          </span>
          <input
            type="number"
            min={1}
            max={50}
            value={batchLimit}
            onChange={(event) => onBatchLimitChange(Number(event.target.value))}
            className="rounded-2xl border border-[var(--line)] bg-white px-4 py-3 outline-none ring-[var(--accent)] transition focus:ring-2"
          />
        </label>

        <label className="flex items-end gap-3 rounded-2xl border border-[var(--line)] bg-white px-4 py-3">
          <input
            type="checkbox"
            checked={settings.sync_drive}
            onChange={(event) => update("sync_drive", event.target.checked)}
            className="h-5 w-5 accent-[var(--accent)]"
          />
          <span className="text-sm font-medium text-[var(--ink)]">Sync Google Drive po zakończeniu</span>
        </label>
      </div>

      <button
        type="button"
        onClick={onRunAll}
        disabled={runningBatch}
        className="mt-8 inline-flex items-center justify-center rounded-full bg-[var(--sage)] px-8 py-4 text-base font-semibold text-white transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {runningBatch ? "Uruchamiam batch..." : `Zbierz batch (${batchLimit} tematów)`}
      </button>
    </section>
  );
}
