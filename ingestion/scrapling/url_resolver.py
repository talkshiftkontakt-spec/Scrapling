from __future__ import annotations

import re
from urllib.parse import urljoin, urlparse, urlunparse

from scrapling.fetchers import DynamicFetcher, Fetcher

TRACKING_QUERY_KEYS = {"ref", "utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term"}


def strip_tracking_params(url: str) -> str:
    parsed = urlparse(url)
    if not parsed.query:
        return url

    pairs = []
    for part in parsed.query.split("&"):
        if not part:
            continue
        key = part.split("=", 1)[0].lower()
        if key in TRACKING_QUERY_KEYS:
            continue
        pairs.append(part)

    cleaned = parsed._replace(query="&".join(pairs))
    return urlunparse(cleaned)


BLOCKED_HOSTS = (
    "awwwards.com",
    "facebook.com",
    "twitter.com",
    "x.com",
    "instagram.com",
    "youtube.com",
    "tiktok.com",
    "linkedin.com",
    "pinterest.",
    "conference.awwwards.com",
)


def is_blocked_host(host: str) -> bool:
    lowered = host.lower()
    return any(blocked in lowered for blocked in BLOCKED_HOSTS)


def resolve_awwwards_external(detail_url: str) -> str | None:
    page = Fetcher.get(detail_url, timeout=30000)
    visit_candidates: list[str] = []
    fallback_candidates: list[str] = []

    for anchor in page.css('a[href^="http"]'):
        href = anchor.attrib.get("href")
        if not href:
            continue

        if any(fragment in href for fragment in ("intent/tweet", "shareArticle", "sharer.php")):
            continue

        host = urlparse(href).netloc.lower()
        if is_blocked_host(host):
            continue

        text = " ".join(anchor.css("::text").getall()).strip().lower()
        if "visit site" in text:
            visit_candidates.append(href)
        else:
            fallback_candidates.append(href)

    if visit_candidates:
        return strip_tracking_params(visit_candidates[0])

    if fallback_candidates:
        return strip_tracking_params(fallback_candidates[0])

    return None


def resolve_landbook_visit(detail_url: str) -> str | None:
    page = DynamicFetcher.fetch(detail_url, headless=True, network_idle=True, timeout=90000)
    for anchor in page.css('a[href^="http"]'):
        text = " ".join(anchor.css("::text").getall()).strip().lower()
        href = anchor.attrib.get("href")
        if href and text == "visit":
            return strip_tracking_params(href)
    return None


def resolve_one_page_love_visit(detail_url: str) -> str | None:
    page = Fetcher.get(detail_url, timeout=30000)
    for anchor in page.css("a"):
        text = " ".join(anchor.css("::text").getall()).strip().lower()
        href = anchor.attrib.get("href")
        if href and href.startswith("http") and "visit website" in text:
            return strip_tracking_params(href)
    return None


def resolve_capture_url(url: str, source: str | None = None) -> str:
    host = urlparse(url).netloc.lower()

    if "awwwards.com/sites/" in url:
        resolved = resolve_awwwards_external(url)
        if resolved:
            return resolved

    if "land-book.com/websites/" in url:
        resolved = resolve_landbook_visit(url)
        if resolved:
            return resolved

    if "onepagelove.com/" in host and "/inspiration" not in url:
        resolved = resolve_one_page_love_visit(url)
        if resolved:
            return resolved

    if source == "landbook" and "land-book.com" in host:
        resolved = resolve_landbook_visit(url)
        if resolved:
            return resolved

    return url


def extract_title_from_url(url: str) -> str:
    slug = urlparse(url).path.rstrip("/").split("/")[-1]
    return slug.replace("-", " ").strip().title() or "Design reference"
