from __future__ import annotations

from ingestion.scrapling.contracts import DiscoveredWebsiteRecord
from ingestion.scrapling.providers.base import SourceProvider
from ingestion.scrapling.url_resolver import extract_title_from_url, resolve_awwwards_external

CATALOG_URLS = [
    "https://www.awwwards.com/websites/",
    "https://www.awwwards.com/websites/sites_of_the_day/",
    "https://www.awwwards.com/websites/nominees/",
    "https://www.awwwards.com/websites/sites_of_the_month/",
    "https://www.awwwards.com/websites/portfolio/",
    "https://www.awwwards.com/websites/animation/",
    "https://www.awwwards.com/websites/single-page/",
    "https://www.awwwards.com/websites/ui-design/",
    "https://www.awwwards.com/websites/e-commerce/",
]


class AwwwardsProvider(SourceProvider):
    slug = "awwwards"
    source_url = CATALOG_URLS[0]

    def discover(self) -> list[DiscoveredWebsiteRecord]:
        records: list[DiscoveredWebsiteRecord] = []
        seen_details: set[str] = set()

        for catalog_url in CATALOG_URLS:
            page = self.fetch_catalog_url(catalog_url)
            for card in page.css('a[href*="/sites/"]'):
                target = card.attrib.get("href")
                if not target or "/sites/" not in target:
                    continue

                slug = target.split("/sites/", 1)[-1].strip("/")
                if not slug or "/" in slug:
                    continue

                detail_url = self.normalize_url(f"/sites/{slug}")
                if detail_url in seen_details:
                    continue
                seen_details.add(detail_url)

                name = " ".join(text.strip() for text in card.css("::text").getall() if text.strip())
                if not name:
                    name = extract_title_from_url(detail_url)

                external_url = resolve_awwwards_external(detail_url)
                if not external_url:
                    continue

                records.append(
                    DiscoveredWebsiteRecord(
                        website_name=name,
                        url=external_url,
                        source=self.slug,
                        categories=[],
                        tags=[],
                        provider_reference=detail_url,
                        metadata={"detailUrl": detail_url, "catalogUrl": catalog_url},
                    )
                )

        return records

    def fetch_catalog_url(self, url: str):
        from scrapling.fetchers import Fetcher

        return Fetcher.get(url, timeout=30000)
