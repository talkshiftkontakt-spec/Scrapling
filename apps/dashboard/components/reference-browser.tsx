"use client";

import { useEffect, useMemo, useState } from "react";

import type { PageScreenshot, PlatformStats, Reference } from "../lib/api";
import { fetchPageScreenshots, getApiUrl, resolveAssetUrl } from "../lib/api";

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
  const [pagesError, setPagesError] = useState<string | null>(null);
  const [expandedUrl, setExpandedUrl] = useState<string | null>(null);

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
    return pageScreenshots
      .filter((page) => page.viewport === viewportFilter)
      .sort((left, right) => left.pagePath.localeCompare(right.pagePath));
  }, [pageScreenshots, viewportFilter]);

  useEffect(() => {
    if (!selected) {
      setPageScreenshots([]);
      setPagesError(null);
      setExpandedUrl(null);
      return;
    }

    let cancelled = false;
    setPagesLoading(true);
    setPagesError(null);

    void fetchPageScreenshots(selected.websiteId)
      .then((pages) => {
        if (cancelled) {
          return;
        }
        setPageScreenshots(pages);
        if (pages.length === 0 && (selected.pageScreenshotCount ?? 0) === 0) {
          setPagesError("Per-page screenshots are still being captured for this site. Refresh in a few minutes.");
        }
      })
      .catch(() => {
        if (!cancelled) {
          setPagesError("Could not load screenshots. Check that the API is running on port 3101.");
        }
      })
      .finally(() => {
        if (!cancelled) {
          setPagesLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [selected]);

  useEffect(() => {
    if (!selected && !expandedUrl) {
      return;
    }

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        if (expandedUrl) {
          setExpandedUrl(null);
        } else {
          setSelected(null);
        }
      }
    };

    document.body.style.overflow = "hidden";
    window.addEventListener("keydown", onKeyDown);
    return () => {
      document.body.style.overflow = "";
      window.removeEventListener("keydown", onKeyDown);
    };
  }, [selected, expandedUrl]);

  const fallbackScreenshotUrl = selected ? resolveAssetUrl(selected.screenshotDriveUrl) : null;
  const hasPageGallery = visiblePages.length > 0;
  const desktopCount = pageScreenshots.filter((page) => page.viewport === "desktop").length;
  const mobileCount = pageScreenshots.filter((page) => page.viewport === "mobile").length;

  return (
    <div className="shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Design Intelligence</p>
          <h1 className="title">Reference Library</h1>
          <p className="subtitle">
            Click any reference to see every page screenshot — full size, desktop and mobile.
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
                    {reference.pageScreenshotCount} shots
                  </span>
                ) : (
                  <span className="card-score" style={{ right: "auto", left: 12, opacity: 0.75 }}>
                    capturing…
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

      {selected ? (
        <div className="modal-backdrop modal-backdrop-full" onClick={() => setSelected(null)} role="presentation">
          <div className="modal modal-full" onClick={(event) => event.stopPropagation()} role="dialog" aria-modal="true">
            <div className="modal-header">
              <div>
                <p className="eyebrow">{selected.source?.replaceAll("_", " ") ?? "reference"}</p>
                <h2 className="title" style={{ fontSize: "1.75rem" }}>
                  {selected.websiteName}
                </h2>
                <p className="subtitle">{selected.canonicalUrl}</p>
              </div>
              <button type="button" className="modal-close" onClick={() => setSelected(null)} aria-label="Close">
                ×
              </button>
            </div>

            <div className="page-toolbar">
              <div className="chip-row">
                <button
                  type="button"
                  className={`chip ${viewportFilter === "desktop" ? "chip-active" : ""}`}
                  onClick={() => setViewportFilter("desktop")}
                >
                  Desktop ({desktopCount || "—"})
                </button>
                <button
                  type="button"
                  className={`chip ${viewportFilter === "mobile" ? "chip-active" : ""}`}
                  onClick={() => setViewportFilter("mobile")}
                >
                  Mobile ({mobileCount || "—"})
                </button>
              </div>
              <p className="page-toolbar-hint">
                {hasPageGallery
                  ? `${visiblePages.length} full screenshots — scroll to see every page`
                  : "Full-size viewport captures"}
              </p>
            </div>

            {pagesLoading ? (
              <div className="empty modal-body-empty">Loading all page screenshots…</div>
            ) : hasPageGallery ? (
              <div className="screenshot-stack">
                {visiblePages.map((page) => {
                  const imageUrl = resolveAssetUrl(page.screenshotDriveUrl);
                  if (!imageUrl) {
                    return null;
                  }

                  return (
                    <section key={page.id} className="screenshot-panel">
                      <header className="screenshot-panel-header">
                        <div>
                          <h3>{page.pageTitle ?? page.pagePath}</h3>
                          <p>
                            {page.pagePath} · {page.pageType} · {page.width}×{page.height}px
                          </p>
                        </div>
                        <div className="screenshot-panel-actions">
                          <button type="button" className="btn" onClick={() => setExpandedUrl(imageUrl)}>
                            Expand
                          </button>
                          <a className="btn" href={imageUrl} target="_blank" rel="noreferrer">
                            Open PNG
                          </a>
                          <a className="btn" href={page.pageUrl} target="_blank" rel="noreferrer">
                            Live page
                          </a>
                        </div>
                      </header>
                      <div className={`screenshot-panel-frame ${viewportFilter === "mobile" ? "screenshot-panel-frame-mobile" : ""}`}>
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img
                          src={imageUrl}
                          alt={`${page.pageType} ${page.pagePath}`}
                          onClick={() => setExpandedUrl(imageUrl)}
                          loading="lazy"
                        />
                      </div>
                    </section>
                  );
                })}
              </div>
            ) : fallbackScreenshotUrl ? (
              <div className="screenshot-stack">
                {pagesError ? <div className="empty modal-body-empty">{pagesError}</div> : null}
                <section className="screenshot-panel">
                  <header className="screenshot-panel-header">
                    <div>
                      <h3>Homepage (legacy capture)</h3>
                      <p>Per-page screenshots are being generated for this site.</p>
                    </div>
                    <div className="screenshot-panel-actions">
                      <button type="button" className="btn" onClick={() => setExpandedUrl(fallbackScreenshotUrl)}>
                        Expand
                      </button>
                      <a className="btn" href={fallbackScreenshotUrl} target="_blank" rel="noreferrer">
                        Open PNG
                      </a>
                    </div>
                  </header>
                  <div className="screenshot-panel-frame">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={fallbackScreenshotUrl}
                      alt={`Screenshot ${selected.websiteName}`}
                      onClick={() => setExpandedUrl(fallbackScreenshotUrl)}
                    />
                  </div>
                </section>
              </div>
            ) : (
              <div className="empty modal-body-empty">
                {pagesError ?? "No screenshots available yet for this reference."}
              </div>
            )}

            <div className="modal-footer">
              <a className="btn btn-primary" href={selected.canonicalUrl} target="_blank" rel="noreferrer">
                Open website
              </a>
              <span className="badge">Score {selected.finalScore?.toFixed(2) ?? "—"}</span>
              {selected.pageScreenshotCount ? (
                <span className="badge">{selected.pageScreenshotCount} screenshots</span>
              ) : null}
              <span className="badge">API {getApiUrl()}</span>
            </div>
          </div>
        </div>
      ) : null}

      {expandedUrl ? (
        <div className="lightbox-backdrop" onClick={() => setExpandedUrl(null)} role="presentation">
          <button type="button" className="lightbox-close" onClick={() => setExpandedUrl(null)} aria-label="Close">
            ×
          </button>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={expandedUrl} alt="Full screenshot" onClick={(event) => event.stopPropagation()} />
        </div>
      ) : null}
    </div>
  );
}
