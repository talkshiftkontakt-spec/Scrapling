from __future__ import annotations

from ingestion.scrapling.contracts import DiscoveredWebsiteRecord
from ingestion.scrapling.providers.base import SourceProvider


class AwwwardsProvider(SourceProvider):
    slug = "awwwards"
    source_url = "https://www.awwwards.com/websites/"

    def discover(self) -> list[DiscoveredWebsiteRecord]:
        page = self.fetch_catalog()
        records: list[DiscoveredWebsiteRecord] = []
        for card in page.css(".js-grid-item"):
            target = card.css("a::attr(href)").get()
            if not target:
                continue
            name = card.css("h3::text").get("Awwwards reference").strip()
            records.append(
                DiscoveredWebsiteRecord(
                    website_name=name,
                    url=self.normalize_url(target),
                    source=self.slug,
                    categories=card.css(".category::text").getall(),
                    tags=card.css(".awards a::text").getall(),
                    provider_reference=target,
                )
            )
        return records
