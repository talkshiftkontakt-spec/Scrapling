"use client";

import { useMemo, useState } from "react";

import type { PlatformStats, Reference } from "../lib/api";
import { getApiUrl, localScreenshotPath, localThumbnailPath } from "../lib/api";

interface ReferenceBrowserProps {
  references: Reference[];
  stats: PlatformStats;
}

export function ReferenceBrowser({ references, stats }: ReferenceBrowserProps) {
  const [query, setQuery] = useState("");
  const [sourceFilter, setSourceFilter] = useState<string>("all");
  const [selected, setSelected] = useState<Reference | null>(null);

  const sources = useMemo(
    () => Array.from(new Set(references.map((item) => item.source).filter(Boolean))) as string[],
    [references]
  );

  const filtered = useMemo(() => {
    const lowered = query.trim().toLowerCase();

    return references.filter((item) => {
      const matchesQuery =
        !lowered ||
        item.websiteName.toLowerCase().includes(lowered) ||
        item.canonicalUrl.toLowerCase().includes(lowered) ||
        item.style?.toLowerCase().includes(lowered) ||
        item.industry?.toLowerCase().includes(lowered);

      const matchesSource = sourceFilter === "all" || item.source === sourceFilter;
      return matchesQuery && matchesSource;
    });
  }, [query, references, sourceFilter]);

  return (
    <div className="shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Design Intelligence</p>
          <h1 className="title">Reference Library</h1>
          <p className="subtitle">
            Przeglądaj zaakceptowane referencje designu — screenshoty, scoring i metadane w jednym miejscu.
          </p>
        </div>

        <div className="stats">
          <div className="stat">
            <span className="stat-value">{stats.accepted ?? references.length}</span>
            <span className="stat-label">Accepted</span>
          </div>
          <div className="stat">
            <span className="stat-value">{stats.discovered ?? "—"}</span>
            <span className="stat-label">In queue</span>
          </div>
        </div>
      </header>

      <div className="toolbar">
        <input
          className="search"
          placeholder="Szukaj po nazwie, URL, stylu, branży…"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
        />
        <div className="chip-row">
          <button
            type="button"
            className={`chip ${sourceFilter === "all" ? "chip-active" : ""}`}
            onClick={() => setSourceFilter("all")}
          >
            Wszystkie
          </button>
          {sources.map((source) => (
            <button
              key={source}
              type="button"
              className={`chip ${sourceFilter === source ? "chip-active" : ""}`}
              onClick={() => setSourceFilter(source)}
            >
              {source.replaceAll("_", " ")}
            </button>
          ))}
        </div>
      </div>

      {filtered.length === 0 ? (
        <div className="empty">Brak referencji pasujących do filtrów.</div>
      ) : (
        <section className="grid">
          {filtered.map((reference) => (
            <button
              key={reference.websiteId}
              type="button"
              className="card"
              onClick={() => setSelected(reference)}
              style={{ textAlign: "left", padding: 0, cursor: "pointer" }}
            >
              <div className="card-media">
                {reference.thumbnailDriveUrl ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={reference.thumbnailDriveUrl} alt={reference.websiteName} loading="lazy" />
                ) : (
                  <div style={{ height: "100%", display: "grid", placeItems: "center", color: "#6b7280" }}>
                    Brak miniatury
                  </div>
                )}
                {reference.finalScore ? <span className="card-score">{reference.finalScore.toFixed(2)}</span> : null}
              </div>
              <div className="card-body">
                <h2 className="card-title">{reference.websiteName}</h2>
                <div className="card-meta">
                  {reference.source ? <span className="badge">{reference.source.replaceAll("_", " ")}</span> : null}
                  {reference.style ? <span className="badge">{reference.style}</span> : null}
                  {reference.industry ? <span className="badge">{reference.industry}</span> : null}
                </div>
                <span className="card-url">{reference.canonicalUrl}</span>
              </div>
            </button>
          ))}
        </section>
      )}

      <section className="storage-panel">
        <h2>Gdzie są zapisane screenshoty?</h2>
        <p>
          Pliki leżą lokalnie w katalogu projektu <code>DesignLibrary/</code> (zmienna <code>DESIGN_LIBRARY_PATH</code>
          w <code>.env</code>).
        </p>
        <p>
          Pełne screenshoty: <code>DesignLibrary/Screenshots/&lt;websiteId&gt;.png</code>
        </p>
        <p>
          Miniatury: <code>DesignLibrary/Thumbnails/&lt;websiteId&gt;-thumb.png</code>
        </p>
        <p>
          API serwuje je pod <code>{getApiUrl()}/static/Screenshots/…</code> i{" "}
          <code>{getApiUrl()}/static/Thumbnails/…</code>
        </p>
        {selected ? (
          <p>
            Przykład dla wybranej karty: <code>{localScreenshotPath(selected.websiteId)}</code>
          </p>
        ) : null}
      </section>

      {selected ? (
        <div className="modal-backdrop" onClick={() => setSelected(null)} role="presentation">
          <div className="modal" onClick={(event) => event.stopPropagation()} role="dialog" aria-modal="true">
            <div className="modal-header">
              <div>
                <p className="eyebrow">{selected.source?.replaceAll("_", " ") ?? "reference"}</p>
                <h2 className="title" style={{ fontSize: "2rem" }}>
                  {selected.websiteName}
                </h2>
                <p className="subtitle">{selected.canonicalUrl}</p>
              </div>
              <button type="button" className="modal-close" onClick={() => setSelected(null)} aria-label="Zamknij">
                ×
              </button>
            </div>

            {selected.screenshotDriveUrl ? (
              <div className="modal-shot">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={selected.screenshotDriveUrl} alt={`Screenshot ${selected.websiteName}`} />
              </div>
            ) : null}

            <div className="modal-footer">
              <a className="btn btn-primary" href={selected.canonicalUrl} target="_blank" rel="noreferrer">
                Otwórz stronę
              </a>
              {selected.screenshotDriveUrl ? (
                <a className="btn" href={selected.screenshotDriveUrl} target="_blank" rel="noreferrer">
                  Otwórz screenshot
                </a>
              ) : null}
              <span className="badge">Score {selected.finalScore?.toFixed(2) ?? "—"}</span>
              {selected.width && selected.height ? (
                <span className="badge">
                  {selected.width} × {selected.height}px
                </span>
              ) : null}
              <span className="badge">{localScreenshotPath(selected.websiteId)}</span>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
