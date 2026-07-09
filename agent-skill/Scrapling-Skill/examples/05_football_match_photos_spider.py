"""
Example 5: Football match action-photo scraper (FootballRoute-oriented)

Collects still ACTION PHOTOS from post-match news pages — not video embeds or
YouTube thumbnails. Designed around FootballRoute's public image layout:

  /images/matches/{home}-vs-{away}-world-cup-2026.jpg      (1600×900 hero)
  /images/blog/{home}-vs-{away}-world-cup-2026-match-recap.jpg

Sources (tested July 2026):
  - theguardian.com/football/live/...  — live blogs publish Getty-style match
    photos within minutes of kick-off; images served from i.guim.co.uk/img/media/

Best for: auto-filling FootballRoute match recap / highlights pages with a
fresh action shot after each fixture.

Outputs:
  - match-photos.json
  - images/matches/ and images/blog/  (with --download)

Usage:
  python 05_football_match_photos_spider.py
  python 05_football_match_photos_spider.py --download
  python 05_football_match_photos_spider.py --seed-url "https://www.theguardian.com/football/live/2026/jul/09/france-v-morocco-world-cup-2026-quarter-final-live"
"""

from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse, urlunparse, parse_qs, urlencode

from scrapling.fetchers import AsyncDynamicSession, FetcherSession
from scrapling.spiders import Request, Response, Spider

GUARDIAN_PHOTO_RE = re.compile(
    r"https://i\.guim\.co\.uk/img/media/[a-f0-9]+/\d+_\d+_\d+_\d+/master/\d+\.jpg",
    re.I,
)
TEAM_SLUG_OVERRIDES = {
    "usa": "usa",
    "us": "usa",
    "united states": "usa",
    "bosnia & herzegovina": "bosnia-and-herzegovina",
    "bosnia and herzegovina": "bosnia-and-herzegovina",
    "türkiye": "turkiye",
    "turkey": "turkiye",
    "south korea": "south-korea",
    "south africa": "south-africa",
    "czechia": "czechia",
    "czech republic": "czechia",
}


def slugify_team(name: str) -> str:
    cleaned = name.strip().lower()
    if cleaned in TEAM_SLUG_OVERRIDES:
        return TEAM_SLUG_OVERRIDES[cleaned]
    slug = re.sub(r"[^a-z0-9]+", "-", cleaned).strip("-")
    return slug or "team"


def footballroute_match_slug(home: str, away: str, tournament: str = "world-cup-2026") -> str:
    return f"{slugify_team(home)}-vs-{slugify_team(away)}-{tournament}"


def upsize_guardian_photo(url: str, width: int = 1600) -> str:
    """Request a larger rendition from Guardian's image CDN."""
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    query["width"] = [str(width)]
    query.setdefault("dpr", ["1"])
    query.setdefault("s", ["none"])
    query.setdefault("crop", ["none"])
    return urlunparse(parsed._replace(query=urlencode(query, doseq=True)))


def extract_teams_from_title(title: str) -> tuple[str, str] | None:
    """Parse 'France 2-0 Morocco' or 'Mexico vs South Africa' style titles."""
    title = re.sub(r"\s*\|.*$", "", title)
    title = re.sub(r"[–—-]\s*live.*$", "", title, flags=re.I).strip()
    title = re.sub(r":\s*world cup.*$", "", title, flags=re.I).strip()
    vs_match = re.search(
        r"([A-Za-zÀ-ÿ .&'-]+?)\s+(?:vs\.?|v)\s+([A-Za-zÀ-ÿ .&'-]+?)(?:\s+\d|\s+live|\s+match|$)",
        title,
        re.I,
    )
    if vs_match:
        return vs_match.group(1).strip(), vs_match.group(2).strip()
    score_match = re.search(r"^([A-Za-zÀ-ÿ .&'-]+?)\s+\d+[-–]\d+\s+([A-Za-zÀ-ÿ .&'-]+)", title)
    if score_match:
        return score_match.group(1).strip(), score_match.group(2).strip()
    return None


def pick_best_photo(urls: list[str]) -> str | None:
    """Prefer the widest master image (largest trailing /NNNN.jpg segment)."""
    best: str | None = None
    best_pixels = -1
    for url in urls:
        master = re.search(r"/master/(\d+)\.jpg", url)
        pixels = int(master.group(1)) if master else 0
        if pixels > best_pixels:
            best_pixels = pixels
            best = url
    return best


class FootballMatchPhotosSpider(Spider):
    name = "football_match_photos"
    concurrent_requests = 2

    def __init__(self, *, seed_urls: list[str] | None = None) -> None:
        super().__init__()
        self.seed_urls = seed_urls or [
            "https://www.theguardian.com/football/world-cup-2026",
        ]
        self._seen_articles: set[str] = set()

    def configure_sessions(self, manager) -> None:
        manager.add("http", FetcherSession(), default=True)
        manager.add(
            "browser",
            AsyncDynamicSession(headless=True, network_idle=True),
            lazy=True,
        )

    async def start_requests(self):
        for url in self.seed_urls:
            sid = "browser" if "theguardian.com" in url else "http"
            if "/live/" in url or "/match-report" in url or "/minute-by-minute" in url:
                yield Request(url, sid=sid, callback=self.parse_article)
            else:
                yield Request(url, sid=sid, callback=self.parse_index)

    async def parse(self, response: Response):
        if False:
            yield {}

    async def parse_index(self, response: Response):
        for href in response.css("a::attr(href)").getall():
            if not href:
                continue
            full = urljoin(response.url, href)
            if "theguardian.com/football/live/" not in full:
                continue
            if "world-cup" not in full.lower():
                continue
            if full in self._seen_articles:
                continue
            self._seen_articles.add(full)
            yield response.follow(full, sid="browser", callback=self.parse_article)

    async def parse_article(self, response: Response):
        photo_urls = [
            src.split(" ")[0]
            for src in response.css("img::attr(src)").getall()
            if src and GUARDIAN_PHOTO_RE.search(src)
        ]
        photo_urls += [
            m.group(0)
            for src in response.css("img::attr(srcset)").getall()
            if src
            for m in GUARDIAN_PHOTO_RE.finditer(src)
        ]
        photo_urls = list(dict.fromkeys(photo_urls))
        best = pick_best_photo(photo_urls)
        if not best:
            return

        title = response.css("title::text").get("").strip()
        teams = extract_teams_from_title(title)
        if not teams:
            h1 = response.css("h1::text").get("").strip()
            teams = extract_teams_from_title(h1)
        if not teams:
            return

        home, away = teams
        match_slug = footballroute_match_slug(home, away)
        image_url = upsize_guardian_photo(best)

        yield {
            "source": "theguardian",
            "title": title,
            "home_team": home,
            "away_team": away,
            "article_url": response.url,
            "image_url": image_url,
            "footballroute_match_image": f"/images/matches/{match_slug}.jpg",
            "footballroute_blog_image": f"/images/blog/{match_slug}-match-recap.jpg",
        }


def download_for_footballroute(items: list[dict], base_dir: Path) -> list[dict]:
    matches_dir = base_dir / "matches"
    blog_dir = base_dir / "blog"
    matches_dir.mkdir(parents=True, exist_ok=True)
    blog_dir.mkdir(parents=True, exist_ok=True)

    with FetcherSession() as session:
        for item in items:
            url = item["image_url"]
            body = session.get(url, timeout=60).body
            if not body:
                item["download_error"] = "empty response"
                continue

            match_name = Path(item["footballroute_match_image"]).name
            blog_name = Path(item["footballroute_blog_image"]).name
            match_path = matches_dir / match_name
            blog_path = blog_dir / blog_name
            match_path.write_bytes(body)
            blog_path.write_bytes(body)
            item["local_match_path"] = str(match_path)
            item["local_blog_path"] = str(blog_path)

    return items


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape football match action photos")
    parser.add_argument(
        "--seed-url",
        action="append",
        dest="seed_urls",
        help="Guardian live blog or WC hub URL (repeatable)",
    )
    parser.add_argument("--download", action="store_true", help="Save images for FootballRoute paths")
    parser.add_argument("--output", default="match-photos.json")
    parser.add_argument("--images-dir", default="images", help="Base dir for matches/ and blog/")
    args = parser.parse_args()

    spider = FootballMatchPhotosSpider(seed_urls=args.seed_urls)
    result = spider.start()
    items = list(result.items)

    if args.download and items:
        items = download_for_footballroute(items, Path(args.images_dir))

    result.items.clear()
    result.items.extend(items)
    result.items.to_json(args.output, indent=True)

    print(f"\n{'=' * 60}")
    print(f"Photos scraped     : {len(items)}")
    print(f"Requests           : {result.stats.requests_count}")
    print(f"Time               : {result.stats.elapsed_seconds:.1f}s")
    print(f"JSON               : {args.output}")
    if args.download:
        print(f"FootballRoute dirs : {args.images_dir}/matches/ + {args.images_dir}/blog/")
    print(f"{'=' * 60}\n")

    for i, item in enumerate(items[:8], 1):
        print(f"{i:>2}. {item['home_team']} vs {item['away_team']}")
        print(f"    match → {item['footballroute_match_image']}")
        print(f"    photo → {item['image_url'][:90]}…")


if __name__ == "__main__":
    main()
