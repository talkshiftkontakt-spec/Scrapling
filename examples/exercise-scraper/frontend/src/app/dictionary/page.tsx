"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { fetchDictionaryTracks, runDictionaryTrack } from "@/lib/api";
import type { DictionaryRunInput, DictionaryTrack } from "@/lib/types";
import { ApiStatusBanner } from "@/components/api-status-banner";
import { DriveStatusBanner } from "@/components/drive-status-banner";

const DEFAULT: DictionaryRunInput = {
  provider: "duckduckgo",
  max_pages: 12,
  top_exercises: 5,
};

export default function DictionaryPage() {
  const router = useRouter();
  const [tracks, setTracks] = useState<DictionaryTrack[]>([]);
  const [settings, setSettings] = useState<DictionaryRunInput>(DEFAULT);
  const [loading, setLoading] = useState(true);
  const [runningId, setRunningId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDictionaryTracks()
      .then(setTracks)
      .catch((err) => setError(err instanceof Error ? err.message : "Błąd wczytywania"))
      .finally(() => setLoading(false));
  }, []);

  async function handleRun(trackId: string) {
    setRunningId(trackId);
    setError(null);
    try {
      const result = await runDictionaryTrack(trackId, settings);
      router.push(`/jobs/${result.job.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nie udało się uruchomić");
    } finally {
      setRunningId(null);
    }
  }

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-8 px-6 py-8">
      <header className="animate-rise">
        <p className="chip bg-[#f8e7cf] text-[#9a6a1d]">Słownictwo EN–PL</p>
        <h1 className="display-title mt-5 text-5xl text-[var(--ink)] sm:text-6xl">
          Słówka i ćwiczenia leksykalne
        </h1>
        <p className="mt-5 max-w-2xl text-lg leading-8 text-[var(--ink-soft)]">
          Listy słówek A1–B1 + wyszukiwanie ćwiczeń tłumaczeniowych z internetu.
          Wynik trafia do <code className="rounded bg-[var(--paper-deep)] px-2 py-0.5 text-sm">grammar-corpus/dictionary/</code>.
        </p>
      </header>

      {error ? (
        <p className="rounded-[1.25rem] bg-[#f6d9d1] px-4 py-3 text-[var(--accent-deep)]">{error}</p>
      ) : null}

      <ApiStatusBanner />
      <DriveStatusBanner />

      <section className="card-surface rounded-[2rem] p-8">
        <h2 className="display-title text-2xl">Ustawienia</h2>
        <div className="mt-4 grid gap-4 md:grid-cols-3">
          <label className="grid gap-2 text-sm">
            Limit stron
            <input
              type="number"
              min={1}
              max={40}
              value={settings.max_pages}
              onChange={(e) => setSettings({ ...settings, max_pages: Number(e.target.value) })}
              className="rounded-2xl border border-[var(--line)] bg-white px-4 py-3"
            />
          </label>
          <label className="grid gap-2 text-sm">
            Top N ćwiczeń
            <input
              type="number"
              min={1}
              max={50}
              value={settings.top_exercises}
              onChange={(e) => setSettings({ ...settings, top_exercises: Number(e.target.value) })}
              className="rounded-2xl border border-[var(--line)] bg-white px-4 py-3"
            />
          </label>
          <label className="grid gap-2 text-sm">
            Wyszukiwarka
            <select
              value={settings.provider}
              onChange={(e) =>
                setSettings({ ...settings, provider: e.target.value as DictionaryRunInput["provider"] })
              }
              className="rounded-2xl border border-[var(--line)] bg-white px-4 py-3"
            >
              <option value="duckduckgo">DuckDuckGo</option>
              <option value="serpapi">SerpAPI</option>
            </select>
          </label>
        </div>
      </section>

      {loading ? (
        <p className="text-[var(--ink-soft)]">Ładuję tracki słownictwa...</p>
      ) : (
        <ul className="grid gap-4 lg:grid-cols-3">
          {tracks.map((track) => (
            <li key={track.id} className="card-surface rounded-[2rem] p-6">
              <p className="chip bg-[var(--sage-soft)] text-[var(--sage)]">{track.level}</p>
              <h3 className="display-title mt-3 text-2xl">{track.description}</h3>
              <p className="mt-2 text-sm text-[var(--ink-soft)]">
                {track.word_count} słów · {track.id}
              </p>
              <button
                type="button"
                disabled={runningId === track.id}
                onClick={() => handleRun(track.id)}
                className="mt-5 rounded-full bg-[var(--accent)] px-5 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
              >
                {runningId === track.id ? "Uruchamiam..." : "Zbierz ćwiczenia"}
              </button>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
