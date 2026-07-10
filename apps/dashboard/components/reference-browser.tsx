"use client";

import { useEffect, useMemo, useState } from "react";

import type { PageScreenshot, PlatformStats, Reference } from "../lib/api";
import { fetchPageScreenshots, getApiUrl, localScreenshotPath, resolveAssetUrl } from "../lib/api";

interface ReferenceBrowserProps {
  references: Reference[];
  stats: PlatformStats;
}

export function ReferenceBrowser({ references, stats }: ReferenceBrowserProps) {
  const [query, setQuery] = useState("");
  const [sourceFilter, setSourceFilter] = useState<string>("all");
  const [selected, setSelected] = useState<Reference | null>(null);
  const [pageScreenshots, setPageScreenshots] = useState<PageScreenshot[]>([]);
  const [viewportFilter, setViewportFilter] = useState<"desktop" | "mobile">("desktop");
  const [pagesLoading, setPagesLoading] = useState(false);

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

  const visiblePages = useMemo(() => {
    const byViewport = pageScreenshots.filter((page) => page.viewport === viewportFilter);
    const uniquePaths = new Map<string, PageScreenshot>();
    for (const page of byViewport) {
      if (!uniquePaths.has(page.pagePath)) {
        uniquePaths.set(page.pagePath, page);
      }
    }
    return Array.from(uniquePaths.values());
  }, [pageScreenshots, viewportFilter]);

  useEffect(() => {
    if (!selected) {
      setPageScreenshots([]);
      return;
    }

    let cancelled = false;
    setPagesLoading(true);
    void fetchPageScreenshots(selected.websiteId).then((pages) => {
      if (!cancelled) {
        setPageScreenshots(pages);
        setPagesLoading(false);
      }
    });

    return () => {
      cancelled = true;
    };
  }, [selected]);

  useEffect(() => {
    if (!selected) {
      return;
    }

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setSelected(null);
      }
    };

    document.body.style.overflow = "hidden";
    window.addEventListener("keydown", onKeyDown);
    return () => {
      document.body.style.overflow = "";
      window.removeEventListener("keydown", onKeyDown);
    };
  }, [selected]);

  const fallbackScreenshotUrl = selected ? resolveAssetUrl(selected.screenshotDriveUrl) : null;
  const hasPageGallery = pageScreenshots.length > 0;
  const desktopCount = pageScreenshots.filter((page) => page.viewport === "desktop").length;
  const mobileCount = pageScreenshots.filter((page) => page.viewport === "mobile").length;

  return (
    <div className="shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Design Intelligence</p>
          <h1 className="title">Reference Library</h1>
          <p className="subtitle">
            Per-page design references — desktop and mobile viewport screenshots for AI-ready design intelligence.
          </p>
        </div>

        <div className="stats">
          <div className="stat">
            <span className="stat-value">{references.length}</span>
            <span className="stat-label">References</span>
          </div>
          <div className="stat">
            <span className="stat-value">{stats.withPageScreenshots ?? references.filter((r) => (r.pageScreenshotCount ?? 0) > 0).length}</span>
            <span className="stat-label">Per-page</span>
          </div>
          <div className="stat">
            <span className="stat-value">{stats.totalPageScreenshots ?? "—"}</span>
            <span className="stat-label">Screenshots</span>
          </div>
        </div>
      </header>

      <div className="toolbar">
        <input
          className="search"
          placeholder="Search by name, URL, style, industry…"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
        />
        <div className="chip-row">
          <button
            type="button"
            className={`chip ${sourceFilter === "all" ? "chip-active" : ""}`}
            onClick={() => setSourceFilter("all")}
          >
            All
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
        <div className="empty">No references match your filters.</div>
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
                  <img src={resolveAssetUrl(reference.thumbnailDriveUrl) ?? ""} alt={reference.websiteName} loading="lazy" />
                ) : (
                  <div style={{ height: "100%", display: "grid", placeItems: "center", color: "#6b7280" }}>
                    No thumbnail
                  </div>
                )}
                {reference.finalScore ? <span className="card-score">{reference.finalScore.toFixed(2)}</span> : null}
                {reference.pageScreenshotCount ? (
                  <span className="card-score" style={{ right: "auto", left: 12, background: "rgba(212,168,83,0.9)", color: "#111" }}>
                    {reference.pageScreenshotCount} pages
                  </span>
                ) : (
                  <span className="card-score" style={{ right: "auto", left: 12, opacity: 0.75 }}>
                    legacy
                  </span>
                )}
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
        <h2>Where screenshots are stored</h2>
        <p>
          Files live in <code>DesignLibrary/</code> (<code>DESIGN_LIBRARY_PATH</code> in <code>.env</code>).
        </p>
        <p>
          Per-page captures: <code>DesignLibrary/PageScreenshots/&lt;websiteId&gt;/desktop|mobile/&lt;page&gt;.png</code>
        </p>
        <p>
          Primary thumbnail: <code>DesignLibrary/Thumbnails/&lt;websiteId&gt;-thumb.png</code>
        </p>
        <p>
          API serves them at <code>{getApiUrl()}/static/PageScreenshots/…</code>
        </p>
      </section>

      {selected ? (
        <div className="modal-backdrop" onClick={() => setSelected(null)} role="presentation">
          <div className="modal modal-wide" onClick={(event) => event.stopPropagation()} role="dialog" aria-modal="true">
            <div className="modal-header">
              <div>
                <p className="eyebrow">{selected.source?.replaceAll("_", " ") ?? "reference"}</p>
                <h2 className="title" style={{ fontSize: "2rem" }}>
                  {selected.websiteName}
                </h2>
                <p className="subtitle">{selected.canonicalUrl}</p>
              </div>
              <button type="button" className="modal-close" onClick={() => setSelected(null)} aria-label="Close">
                ×
              </button>
            </div>

            {hasPageGallery ? (
              <>
                <div className="page-toolbar">
                  <div className="chip-row">
                    <button
                      type="button"
                      className={`chip ${viewportFilter === "desktop" ? "chip-active" : ""}`}
                      onClick={() => setViewportFilter("desktop")}
                    >
                      Desktop ({desktopCount})
                    </button>
                    <button
                      type="button"
                      className={`chip ${viewportFilter === "mobile" ? "chip-active" : ""}`}
                      onClick={() => setViewportFilter("mobile")}
                    >
                      Mobile ({mobileCount})
                    </button>
                  </div>
                  <p className="page-toolbar-hint">
                    {visiblePages.length} page{visiblePages.length === 1 ? "" : "s"} · viewport screenshot (not full scroll)
                  </p>
                </div>
                <div className="page-gallery">
                  {visiblePages.map((page) => {
                    const imageUrl = resolveAssetUrl(page.screenshotDriveUrl);
                    return (
                      <article key={page.id} className="page-shot-card">
                        <div
                          className={`page-shot-frame ${viewportFilter === "mobile" ? "page-shot-frame-mobile" : "page-shot-frame-desktop"}`}
                        >
                          {imageUrl ? (
                            // eslint-disable-next-line @next/next/no-img-element
                            <img
                              src={imageUrl}
                              alt={`${page.pageType} ${page.pagePath}`}
                              onClick={() => window.open(imageUrl, "_blank", "noopener,noreferrer")}
                              title="Click to open full image"
                            />
                          ) : null}
                        </div>
                        <div className="page-shot-meta">
                          <strong>{page.pageTitle ?? page.pagePath}</strong>
                          <span className="badge">{page.pageType}</span>
                          <span className="badge">{page.pagePath}</span>
                          <span className="badge">
                            {page.width} × {page.height}px
                          </span>
                        </div>
                      </article>
                    );
                  })}
                </div>
              </>
            ) : pagesLoading ? (
              <div className="empty" style={{ margin: "24px" }}>
                Loading page screenshots…
              </div>
            ) : fallbackScreenshotUrl ? (
              <div className="modal-shot-scroll">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={fallbackScreenshotUrl}
                  alt={`Screenshot ${selected.websiteName}`}
                  onClick={() => window.open(fallbackScreenshotUrl, "_blank", "noopener,noreferrer")}
                  title="Legacy single screenshot — run recapture for per-page shots"
                />
              </div>
            ) : null}

            <div className="modal-footer">
              <a className="btn btn-primary" href={selected.canonicalUrl} target="_blank" rel="noreferrer">
                Open website
              </a>
              <span className="badge">Score {selected.finalScore?.toFixed(2) ?? "—"}</span>
              {selected.pageScreenshotCount ? (
                <span className="badge">{selected.pageScreenshotCount} page screenshots</span>
              ) : null}
              <span className="badge">{localScreenshotPath(selected.websiteId)}</span>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
