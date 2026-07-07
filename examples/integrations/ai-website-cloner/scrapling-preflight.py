#!/usr/bin/env python3
"""
Pre-flight a clone target URL with Scrapling before running /clone-website.

Checks HTTP reachability, detects thin SPA shells, lists internal links.

Usage:
  pip install "scrapling[fetchers]"
  python scripts/scrapling-preflight.py https://example.com
  python scripts/scrapling-preflight.py https://www.lingology.pl --dynamic
"""

from __future__ import annotations

import argparse
import sys
from urllib.parse import urljoin, urlparse

from scrapling.fetchers import DynamicFetcher, Fetcher


def analyze(url: str, *, dynamic: bool) -> int:
    print(f"\n🔍 Scrapling preflight: {url}\n")

    if dynamic:
        page = DynamicFetcher.fetch(url, headless=True, network_idle=True, timeout=45000)
        mode = "dynamic"
    else:
        page = Fetcher.get(url, stealthy_headers=True, timeout=30)
        mode = "fetcher"

    print(f"Status     : {page.status}")
    print(f"Mode       : {mode}")
    title = page.css("title::text").get() or "(no title)"
    print(f"Title      : {title[:80]}")

    h1 = page.css("h1::text").getall()
    text_len = len(page.get_all_text(ignore_tags=("script", "style")))

    print(f"H1 count   : {len(h1)}")
    print(f"Text chars : {text_len}")

    if text_len < 400:
        print("\n⚠️  Thin page — likely SPA. Re-run with --dynamic or use browser MCP in clone skill.")

    host = urlparse(url).netloc
    links: list[str] = []
    for href in page.css("a::attr(href)").getall()[:200]:
        full = urljoin(url, href)
        if urlparse(full).netloc == host:
            links.append(full.split("#")[0])

    unique = sorted(set(links))[:15]
    if unique:
        print("\nInternal links (sample):")
        for link in unique:
            print(f"  - {link}")

    if page.status != 200:
        return 1
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrapling preflight for website cloner")
    parser.add_argument("url")
    parser.add_argument("--dynamic", action="store_true", help="Use DynamicFetcher")
    args = parser.parse_args()
    sys.exit(analyze(args.url, dynamic=args.dynamic))


if __name__ == "__main__":
    main()
