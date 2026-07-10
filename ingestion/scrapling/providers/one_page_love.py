from __future__ import annotations

from ingestion.scrapling.contracts import DiscoveredWebsiteRecord
from ingestion.scrapling.providers.base import SourceProvider


class OnePageLoveProvider(SourceProvider):
    slug = "one_page_love"
    source_url = "https://onepagelove.com/inspiration"

    def discover(self) -> list[DiscoveredWebsiteRecord]:
        page = self.fetch_catalog()
        records: list[DiscoveredWebsiteRecord] = []
        for card in page.css("a[href*='/inspiration/']"):
            target = card.attrib.get("href")
            if not target:
                continue
            title = card.css("img::attr(alt)").get("One Page Love reference").strip()
            records.append(
                DiscoveredWebsiteRecord(
                    website_name=title,
                    url=self.normalize_url(target),
                    source=self.slug,
                    categories=[],
                    tags=[],
                    provider_reference=target,
                )
            )
        return records
