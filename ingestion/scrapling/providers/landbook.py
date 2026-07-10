from __future__ import annotations

from ingestion.scrapling.contracts import DiscoveredWebsiteRecord
from ingestion.scrapling.providers.base import SourceProvider


class LandbookProvider(SourceProvider):
    slug = "landbook"
    source_url = "https://land-book.com/"

    def discover(self) -> list[DiscoveredWebsiteRecord]:
        page = self.fetch_catalog()
        records: list[DiscoveredWebsiteRecord] = []
        for card in page.css("a[href*='/gallery/']"):
            target = card.attrib.get("href")
            if not target:
                continue
            label = card.css("img::attr(alt)").get("Land-book reference").strip()
            records.append(
                DiscoveredWebsiteRecord(
                    website_name=label,
                    url=self.normalize_url(target),
                    source=self.slug,
                    categories=[],
                    tags=[],
                    provider_reference=target,
                )
            )
        return records
