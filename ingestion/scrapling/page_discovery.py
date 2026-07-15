from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse, urlunparse


COMMON_PATHS = [
    "/",
    "/pricing",
    "/plans",
    "/about",
    "/about-us",
    "/features",
    "/product",
    "/contact",
    "/blog",
    "/login",
    "/sign-in",
    "/signup",
    "/dashboard",
    "/app",
]

PAGE_TYPE_PATTERNS: list[tuple[str, str]] = [
    (r"^/$", "home"),
    (r"^/pricing|^/plans|^/price", "pricing"),
    (r"^/about", "about"),
    (r"^/features|^/product|^/solutions", "features"),
    (r"^/contact", "contact"),
    (r"^/blog|^/news|^/articles", "blog"),
    (r"^/login|^/sign-?in|^/auth", "login"),
    (r"^/dashboard|^/app(?:/|$)", "dashboard"),
    (r"^/privacy|^/terms|^/legal|^/imprint", "legal"),
    (r"^/careers|^/jobs", "careers"),
]

SKIP_EXTENSIONS = {
    ".pdf",
    ".zip",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".webp",
    ".mp4",
    ".mp3",
    ".css",
    ".js",
    ".json",
    ".xml",
}


@dataclass(slots=True)
class DiscoveredPage:
    page_url: str
    page_path: str
    page_type: str
    priority: int


def normalize_path(path: str) -> str:
    if not path or path == "/":
        return "/"
    cleaned = path.split("?")[0].split("#")[0].rstrip("/")
    return cleaned if cleaned else "/"


def infer_page_type(page_path: str) -> str:
    for pattern, page_type in PAGE_TYPE_PATTERNS:
        if re.search(pattern, page_path, flags=re.IGNORECASE):
            return page_type
    return "page"


def path_priority(page_path: str, page_type: str) -> int:
    if page_type == "home":
        return 0
    priority_map = {
        "pricing": 1,
        "features": 2,
        "about": 3,
        "contact": 4,
        "blog": 5,
        "login": 6,
        "dashboard": 7,
        "careers": 8,
        "legal": 9,
        "page": 10,
    }
    return priority_map.get(page_type, 10)


def same_origin(base_url: str, candidate_url: str) -> bool:
    base = urlparse(base_url)
    candidate = urlparse(candidate_url)
    return candidate.netloc == base.netloc or not candidate.netloc


def build_page_url(base_url: str, page_path: str) -> str:
    parsed = urlparse(base_url)
    normalized_path = page_path if page_path.startswith("/") else f"/{page_path}"
    return urlunparse((parsed.scheme, parsed.netloc, normalized_path, "", "", ""))


def should_skip_href(href: str) -> bool:
    lowered = href.lower().strip()
    if not lowered or lowered.startswith("#"):
        return True
    if lowered.startswith(("mailto:", "tel:", "javascript:", "data:")):
        return True
    for extension in SKIP_EXTENSIONS:
        if lowered.endswith(extension):
            return True
    return False


def discover_pages_from_links(base_url: str, hrefs: list[str], max_pages: int) -> list[DiscoveredPage]:
    discovered: dict[str, DiscoveredPage] = {}

    def add_page(page_path: str) -> None:
        normalized = normalize_path(page_path)
        page_type = infer_page_type(normalized)
        page_url = build_page_url(base_url, normalized)
        priority = path_priority(normalized, page_type)
        existing = discovered.get(normalized)
        if existing is None or priority < existing.priority:
            discovered[normalized] = DiscoveredPage(
                page_url=page_url,
                page_path=normalized,
                page_type=page_type,
                priority=priority,
            )

    add_page("/")

    for href in hrefs:
        if should_skip_href(href):
            continue
        absolute = urljoin(base_url, href)
        if not same_origin(base_url, absolute):
            continue
        parsed = urlparse(absolute)
        add_page(parsed.path or "/")

    ordered = sorted(discovered.values(), key=lambda item: (item.priority, item.page_path))
    return ordered[:max_pages]


def discover_pages_in_browser(page, base_url: str, max_pages: int) -> list[DiscoveredPage]:
    hrefs: list[str] = page.evaluate(
        """
        () => Array.from(document.querySelectorAll('a[href]'))
          .map((anchor) => anchor.getAttribute('href'))
          .filter(Boolean)
        """
    )
    return discover_pages_from_links(base_url, hrefs, max_pages=max_pages)
