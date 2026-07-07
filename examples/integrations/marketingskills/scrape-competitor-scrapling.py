#!/usr/bin/env python3
"""
Scrape competitor pages with Scrapling → competitor-profiles/raw/ layout.

Example (Lingology vs language-learning competitor):
  python scripts/scrape-competitor-scrapling.py \\
    --slug duolingo \\
    --url https://www.duolingo.com \\
    --pages /,/premium

Requires: pip install "scrapling[fetchers]"
Optional: scrapling install  (for --dynamic)
"""

from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path

from scrapling.fetchers import DynamicFetcher, Fetcher


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def fetch_page(url: str, *, dynamic: bool) -> str:
    if dynamic:
        page = DynamicFetcher.fetch(url, headless=True, network_idle=True, timeout=45000)
    else:
        page = Fetcher.get(url, stealthy_headers=True, timeout=30)
    if page.status != 200:
        raise RuntimeError(f"HTTP {page.status} for {url}")
    return page.get_all_text(ignore_tags=("script", "style", "nav", "footer", "svg"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Competitor scrape via Scrapling")
    parser.add_argument("--slug", required=True, help="competitor-profiles slug, e.g. buki")
    parser.add_argument("--url", required=True, help="Base URL, e.g. https://example.com")
    parser.add_argument(
        "--pages",
        default="/,/pricing,/features",
        help="Comma-separated paths (default: /,/pricing,/features)",
    )
    parser.add_argument("--dynamic", action="store_true", help="Use DynamicFetcher (SPAs)")
    parser.add_argument("--out", default="competitor-profiles", help="Output root dir")
    args = parser.parse_args()

    base = args.url.rstrip("/")
    day = date.today().isoformat()
    out_dir = Path(args.out) / "raw" / args.slug / day / "scrapes"
    out_dir.mkdir(parents=True, exist_ok=True)

    for path in [p.strip() for p in args.pages.split(",") if p.strip()]:
        page_url = base if path == "/" else f"{base}{path}"
        name = "homepage" if path == "/" else slugify(path.strip("/")) or "page"
        print(f"Scraping {page_url} → {name}.md")
        text = fetch_page(page_url, dynamic=args.dynamic)
        (out_dir / f"{name}.md").write_text(
            f"# {page_url}\n\n{text[:50000]}",
            encoding="utf-8",
        )

    print(f"Done. Raw scrapes: {out_dir}")


if __name__ == "__main__":
    main()
