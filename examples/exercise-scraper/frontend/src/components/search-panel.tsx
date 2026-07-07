"use client";

import { useState } from "react";
import type { CreateJobInput, LangMode, ProviderMode } from "@/lib/types";

interface SearchPanelProps {
  loading: boolean;
  onSubmit: (input: CreateJobInput) => Promise<void>;
}

export function SearchPanel({ loading, onSubmit }: SearchPanelProps) {
  const [topic, setTopic] = useState("Past Simple");
  const [topicPl, setTopicPl] = useState("");
  const [topicEn, setTopicEn] = useState("");
  const [lang, setLang] = useState<LangMode>("both");
  const [provider, setProvider] = useState<ProviderMode>("duckduckgo");
  const [maxPages, setMaxPages] = useState(15);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await onSubmit({
      topic,
      lang,
      provider,
      max_pages: maxPages,
      topic_pl: topicPl || undefined,
      topic_en: topicEn || undefined,
    });
  }

  return (
    <form onSubmit={handleSubmit} className="card-surface animate-rise rounded-[2rem] p-8">
      <div className="mb-8">
        <p className="chip bg-[var(--sage-soft)] text-[var(--sage)]">Nowe zbieranie</p>
        <h2 className="display-title mt-4 text-4xl text-[var(--ink)]">Wpisz temat gramatyki</h2>
        <p className="mt-3 max-w-2xl text-base leading-7 text-[var(--ink-soft)]">
          Narzędzie przeszuka internet, pobierze strony z ćwiczeniami i zapisze gotowe zadania w jednym miejscu.
        </p>
      </div>

      <div className="grid gap-5">
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

        <div className="grid gap-5 md:grid-cols-3">
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
        </div>
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
