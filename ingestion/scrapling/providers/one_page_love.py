from __future__ import annotations

import re

from scrapling.fetchers import Fetcher

from ingestion.scrapling.contracts import DiscoveredWebsiteRecord
from ingestion.scrapling.providers.base import SourceProvider
from ingestion.scrapling.url_resolver import extract_title_from_url, resolve_one_page_love_visit, strip_tracking_params

SITEMAP_URLS = [
    "https://onepagelove.com/post_part1.xml",
    "https://onepagelove.com/post_part2.xml",
]


class OnePageLoveProvider(SourceProvider):
    slug = "one_page_love"
    source_url = "https://onepagelove.com/feed"
    max_posts = 80

    def discover(self) -> list[DiscoveredWebsiteRecord]:
        detail_urls: list[str] = []
        seen: set[str] = set()

        for sitemap_url in SITEMAP_URLS:
            page = Fetcher.get(sitemap_url, timeout=30000)
            content = page.body.decode("utf-8", errors="ignore") if isinstance(page.body, bytes) else str(page.body)
            for match in re.findall(r"<loc>(https://onepagelove\.com/[a-z0-9-]+)</loc>", content):
                if match in seen:
                    continue
                seen.add(match)
                detail_urls.append(match)
                if len(detail_urls) >= self.max_posts:
                    break
            if len(detail_urls) >= self.max_posts:
                break

        records: list[DiscoveredWebsiteRecord] = []
        for detail_url in detail_urls:
            external_url = resolve_one_page_love_visit(detail_url)
            if not external_url:
                continue

            slug = detail_url.rstrip("/").split("/")[-1]
            records.append(
                DiscoveredWebsiteRecord(
                    website_name=extract_title_from_url(slug),
                    url=strip_tracking_params(external_url),
                    source=self.slug,
                    categories=[],
                    tags=[],
                    provider_reference=detail_url,
                    metadata={"detailUrl": detail_url},
                )
            )

        return records
