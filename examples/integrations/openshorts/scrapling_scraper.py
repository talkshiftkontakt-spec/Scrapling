"""
Website scraping for SaaSShorts via Scrapling (with httpx fallback).

Modes (env SAASSHORTS_SCRAPE_MODE):
  auto    — Fetcher first, DynamicFetcher if page looks empty (default)
  static  — Scrapling Fetcher only (fast, no browser)
  dynamic — Scrapling DynamicFetcher (JS / SPAs)
  legacy  — original httpx + BeautifulSoup only
"""

from __future__ import annotations

import os
import re
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

SUBPAGE_KEYWORDS = (
    "pricing",
    "features",
    "about",
    "product",
    "why",
    "how-it-works",
    "use-case",
    "plans",
    "cennik",
    "oferta",
    "cena",
)


def _response_html(page) -> str:
    body = page.body
    if isinstance(body, bytes):
        return body.decode("utf-8", errors="replace")
    return str(body)


def _is_sparse(soup: BeautifulSoup) -> bool:
    text = soup.get_text(strip=True)
    has_h1 = soup.find("h1") is not None
    return len(text) < 400 or not has_h1


def fetch_html(url: str) -> tuple[str, str]:
    """Return (html, mode_label)."""
    mode = os.environ.get("SAASSHORTS_SCRAPE_MODE", "auto").lower()

    if mode == "legacy":
        return _fetch_html_legacy(url), "legacy-httpx"

    if mode in ("static", "auto"):
        try:
            from scrapling.fetchers import Fetcher

            page = Fetcher.get(url, stealthy_headers=True, timeout=30)
            if page.status == 200:
                html = _response_html(page)
                soup = BeautifulSoup(html, "html.parser")
                if mode == "static" or not _is_sparse(soup):
                    return html, "scrapling-fetcher"
                if mode == "static":
                    return html, "scrapling-fetcher-sparse"
        except Exception as exc:
            print(f"[SaaSShorts]   ⚠️ Scrapling Fetcher: {exc}")

    if mode in ("dynamic", "auto"):
        try:
            from scrapling.fetchers import DynamicFetcher

            page = DynamicFetcher.fetch(
                url,
                headless=True,
                network_idle=True,
                timeout=45000,
                load_dom=True,
            )
            if page.status == 200:
                return _response_html(page), "scrapling-dynamic"
        except Exception as exc:
            print(f"[SaaSShorts]   ⚠️ Scrapling DynamicFetcher: {exc}")

    return _fetch_html_legacy(url), "legacy-httpx-fallback"


def _fetch_html_legacy(url: str) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }
    with httpx.Client(timeout=30.0, follow_redirects=True) as client:
        response = client.get(url, headers=headers)
        response.raise_for_status()
        return response.text


def _extract_from_soup(soup: BeautifulSoup, url: str) -> dict:
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "svg", "iframe"]):
        tag.decompose()

    meta_desc = ""
    meta_tag = soup.find("meta", attrs={"name": "description"})
    if meta_tag:
        meta_desc = meta_tag.get("content", "") or ""

    og_desc = ""
    og_tag = soup.find("meta", attrs={"property": "og:description"})
    if og_tag:
        og_desc = og_tag.get("content", "") or ""

    title = soup.title.string.strip() if soup.title and soup.title.string else ""

    headings: list[str] = []
    for heading in soup.find_all(["h1", "h2", "h3"]):
        text = heading.get_text(strip=True)
        if text and len(text) < 200:
            headings.append(text)

    text = soup.get_text(separator="\n", strip=True)
    text = re.sub(r"\n{3,}", "\n\n", text)[:10000]

    base_host = httpx.URL(url).host
    subpages: set[str] = set()
    for anchor in soup.find_all("a", href=True):
        href = anchor["href"].lower()
        if any(keyword in href for keyword in SUBPAGE_KEYWORDS):
            try:
                full_url = urljoin(url, anchor["href"])
                if httpx.URL(full_url).host == base_host:
                    subpages.add(full_url)
            except Exception:
                pass

    return {
        "title": title,
        "meta_description": meta_desc or og_desc,
        "headings": headings[:20],
        "main_content": text,
        "subpages": list(subpages),
    }


def scrape_website(url: str) -> dict:
    """Drop-in replacement for SaaSShorts website scraping."""
    print(f"[SaaSShorts] 🌐 Scraping {url} (Scrapling pipeline)...")

    html, mode = fetch_html(url)
    print(f"[SaaSShorts]   Mode: {mode}")

    parsed = _extract_from_soup(BeautifulSoup(html, "html.parser"), url)

    additional = ""
    subpages_scraped = 0
    for sub_url in parsed["subpages"][:3]:
        try:
            print(f"[SaaSShorts]   → Subpage: {sub_url}")
            sub_html, _ = fetch_html(sub_url)
            sub_parsed = _extract_from_soup(BeautifulSoup(sub_html, "html.parser"), sub_url)
            chunk = sub_parsed["main_content"][:5000]
            additional += f"\n\n--- {sub_url} ---\n{chunk}"
            subpages_scraped += 1
        except Exception as exc:
            print(f"[SaaSShorts]   ⚠️ Subpage failed: {exc}")

    result = {
        "url": url,
        "title": parsed["title"],
        "meta_description": parsed["meta_description"],
        "headings": parsed["headings"],
        "main_content": parsed["main_content"],
        "additional_pages": additional[:15000],
        "pages_scraped": 1 + subpages_scraped,
        "scrape_mode": mode,
    }

    print(
        f"[SaaSShorts] ✅ Scraped {result['pages_scraped']} pages, "
        f"{len(parsed['main_content'])} chars ({mode})"
    )
    return result
