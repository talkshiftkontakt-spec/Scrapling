from __future__ import annotations

from ingestion.scrapling.contracts import DiscoveredWebsiteRecord
from ingestion.scrapling.providers.base import SourceProvider


class GodlyProvider(SourceProvider):
    slug = "godly"
    source_url = "https://godly.website/"

    def discover(self) -> list[DiscoveredWebsiteRecord]:
        page = self.fetch_catalog()
        records: list[DiscoveredWebsiteRecord] = []
        for card in page.css("a[href*='/website/']"):
            target = card.attrib.get("href")
            if not target:
                continue
            title = card.css("h3::text").get("Godly reference").strip()
            records.append(
                DiscoveredWebsiteRecord(
                    website_name=title,
                    url=self.normalize_url(target),
                    source=self.slug,
                    categories=[],
                    tags=card.css("span::text").getall(),
                    provider_reference=target,
                )
            )
        return records
