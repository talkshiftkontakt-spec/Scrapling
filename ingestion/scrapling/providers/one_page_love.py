from __future__ import annotations

import re

from scrapling.fetchers import Fetcher

from ingestion.scrapling.contracts import DiscoveredWebsiteRecord
from ingestion.scrapling.providers.base import SourceProvider
from ingestion.scrapling.url_resolver import extract_title_from_url, resolve_one_page_love_visit, strip_tracking_params


class OnePageLoveProvider(SourceProvider):
    slug = "one_page_love"
    source_url = "https://onepagelove.com/feed"

    def discover(self) -> list[DiscoveredWebsiteRecord]:
        page = Fetcher.get(self.source_url, timeout=30000)
        content = page.body.decode("utf-8", errors="ignore") if isinstance(page.body, bytes) else str(page.body)
        detail_urls = []
        seen: set[str] = set()

        for match in re.findall(r"<link>(https://onepagelove\.com/[a-z0-9-]+)</link>", content):
            if match in seen or match.endswith("onepagelove.com"):
                continue
            seen.add(match)
            detail_urls.append(match)

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
