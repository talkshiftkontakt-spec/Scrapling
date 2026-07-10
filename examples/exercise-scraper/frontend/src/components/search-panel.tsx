"use client";

import { useEffect, useState } from "react";
import { fetchCorpusTopics } from "@/lib/api";
import type { CorpusTopic, CreateJobInput, LangMode, ProviderMode } from "@/lib/types";

interface SearchPanelProps {
  loading: boolean;
  onSubmit: (input: CreateJobInput) => Promise<void>;
}

export function SearchPanel({ loading, onSubmit }: SearchPanelProps) {
  const [topic, setTopic] = useState("Past Simple");
  const [topicPl, setTopicPl] = useState("");
  const [topicEn, setTopicEn] = useState("");
  const [topicId, setTopicId] = useState("");
  const [taxonomy, setTaxonomy] = useState<CorpusTopic[]>([]);
  const [lang, setLang] = useState<LangMode>("both");
  const [provider, setProvider] = useState<ProviderMode>("duckduckgo");
  const [maxPages, setMaxPages] = useState(15);
  const [topN, setTopN] = useState(3);
  const [syncDrive, setSyncDrive] = useState(false);

  useEffect(() => {
    fetchCorpusTopics()
      .then(setTaxonomy)
      .catch(() => undefined);
  }, []);

  useEffect(() => {
    if (!topicId) return;
    const entry = taxonomy.find((item) => item.id === topicId);
    if (!entry) return;
    setTopic(entry.en[0] ?? topic);
    setTopicEn(entry.en[0] ?? "");
    setTopicPl(entry.pl[0] ?? "");
  }, [topicId, taxonomy, topic]);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await onSubmit({
      topic,
      lang,
      provider,
      max_pages: maxPages,
      topic_pl: topicPl || undefined,
      topic_en: topicEn || undefined,
      topic_id: topicId || undefined,
      top_exercises: topN,
      sync_drive: syncDrive,
    });
  }

  return (
    <form onSubmit={handleSubmit} className="card-surface animate-rise rounded-[2rem] p-8">
      <div className="mb-8">
        <p className="chip bg-[var(--sage-soft)] text-[var(--sage)]">Nowe zbieranie</p>
        <h2 className="display-title mt-4 text-4xl text-[var(--ink)]">Wpisz temat gramatyki</h2>
        <p className="mt-3 max-w-2xl text-base leading-7 text-[var(--ink-soft)]">
          Opcjonalnie wybierz temat z taksonomii — włączy walidator gramatyczny i zapis do korpusu.
        </p>
      </div>

      <div className="grid gap-5">
        <label className="grid gap-2">
          <span className="text-sm font-semibold uppercase tracking-[0.18em] text-[var(--ink-soft)]">
            Temat z taksonomii (opcjonalnie)
          </span>
          <select
            value={topicId}
            onChange={(event) => setTopicId(event.target.value)}
            className="rounded-2xl border border-[var(--line)] bg-white px-4 py-3 outline-none ring-[var(--accent)] transition focus:ring-2"
          >
            <option value="">— dowolna fraza —</option>
            {taxonomy.map((entry) => (
              <option key={entry.id} value={entry.id}>
                {entry.level} · {entry.en[0]} ({entry.id})
              </option>
            ))}
          </select>
        </label>

        <label className="grid gap-2">
          <span className="text-sm font-semibold uppercase tracking-[0.18em] text-[var(--ink-soft)]">
            Główna fraza
          </span>
          <input
            value={topic}
            onChange={(event) => setTopic(event.target.value)}
            className="rounded-2xl border border-[var(--line)] bg-white px-4 py-3 text-lg outline-none ring-[var(--accent)] transition focus:ring-2"
            placeholder="Past Simple"
            required
          />
        </label>

        <div className="grid gap-5 md:grid-cols-2">
          <label className="grid gap-2">
            <span className="text-sm font-semibold uppercase tracking-[0.18em] text-[var(--ink-soft)]">
              Fraza po polsku
            </span>
            <input
              value={topicPl}
              onChange={(event) => setTopicPl(event.target.value)}
              className="rounded-2xl border border-[var(--line)] bg-white px-4 py-3 outline-none ring-[var(--accent)] transition focus:ring-2"
              placeholder="czas Past Simple zadania"
            />
          </label>
          <label className="grid gap-2">
            <span className="text-sm font-semibold uppercase tracking-[0.18em] text-[var(--ink-soft)]">
              Fraza po angielsku
            </span>
            <input
              value={topicEn}
              onChange={(event) => setTopicEn(event.target.value)}
              className="rounded-2xl border border-[var(--line)] bg-white px-4 py-3 outline-none ring-[var(--accent)] transition focus:ring-2"
              placeholder="Past Simple exercises"
            />
          </label>
        </div>

        <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-4">
          <label className="grid gap-2">
            <span className="text-sm font-semibold uppercase tracking-[0.18em] text-[var(--ink-soft)]">
              Język źródeł
            </span>
            <select
              value={lang}
              onChange={(event) => setLang(event.target.value as LangMode)}
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
              value={provider}
              onChange={(event) => setProvider(event.target.value as ProviderMode)}
              className="rounded-2xl border border-[var(--line)] bg-white px-4 py-3 outline-none ring-[var(--accent)] transition focus:ring-2"
            >
              <option value="duckduckgo">DuckDuckGo</option>
              <option value="serpapi">SerpAPI</option>
            </select>
          </label>

          <label className="grid gap-2">
            <span className="text-sm font-semibold uppercase tracking-[0.18em] text-[var(--ink-soft)]">
              Limit stron
            </span>
            <input
              type="number"
              min={1}
              max={60}
              value={maxPages}
              onChange={(event) => setMaxPages(Number(event.target.value))}
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
              value={topN}
              onChange={(event) => setTopN(Number(event.target.value))}
              className="rounded-2xl border border-[var(--line)] bg-white px-4 py-3 outline-none ring-[var(--accent)] transition focus:ring-2"
            />
          </label>
        </div>

        <label className="flex items-center gap-3 rounded-2xl border border-[var(--line)] bg-white px-4 py-3">
          <input
            type="checkbox"
            checked={syncDrive}
            onChange={(event) => setSyncDrive(event.target.checked)}
            className="h-5 w-5 accent-[var(--accent)]"
          />
          <span className="text-sm font-medium text-[var(--ink)]">Synchronizuj z Google Drive po zakończeniu</span>
        </label>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="mt-8 inline-flex items-center justify-center rounded-full bg-[var(--accent)] px-8 py-4 text-base font-semibold text-white transition hover:bg-[var(--accent-deep)] disabled:cursor-not-allowed disabled:opacity-60"
      >
        {loading ? "Uruchamiam zbieranie..." : "Zbierz ćwiczenia"}
      </button>
    </form>
  );
}
