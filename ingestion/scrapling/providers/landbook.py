from __future__ import annotations

from scrapling.fetchers import Fetcher

from ingestion.scrapling.contracts import DiscoveredWebsiteRecord
from ingestion.scrapling.providers.base import SourceProvider
from ingestion.scrapling.url_resolver import extract_title_from_url


class LandbookProvider(SourceProvider):
    slug = "landbook"
    source_url = "https://land-book.com/"
    max_pages = 8

    def discover(self) -> list[DiscoveredWebsiteRecord]:
        records: list[DiscoveredWebsiteRecord] = []
        seen_details: set[str] = set()

        for page_number in range(1, self.max_pages + 1):
            catalog_url = self.source_url if page_number == 1 else f"{self.source_url}?page={page_number}"
            page = Fetcher.get(catalog_url, timeout=30000)

            for card in page.css('a[href^="/websites/"]'):
                target = card.attrib.get("href")
                if not target or "#" in target:
                    continue

                detail_url = self.normalize_url(target.split("#", 1)[0])
                if detail_url in seen_details:
                    continue
                seen_details.add(detail_url)

                label = card.css("img::attr(alt)").get("").strip()
                if not label:
                    label = extract_title_from_url(detail_url)

                records.append(
                    DiscoveredWebsiteRecord(
                        website_name=label.split(" - ")[0].strip(),
                        url=detail_url,
                        source=self.slug,
                        categories=[],
                        tags=[],
                        provider_reference=detail_url,
                        metadata={"detailUrl": detail_url, "resolveAtCapture": True},
                    )
                )

        return records
