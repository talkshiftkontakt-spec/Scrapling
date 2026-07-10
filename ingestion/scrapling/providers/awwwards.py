from __future__ import annotations

from ingestion.scrapling.contracts import DiscoveredWebsiteRecord
from ingestion.scrapling.providers.base import SourceProvider
from ingestion.scrapling.url_resolver import extract_title_from_url, resolve_awwwards_external


class AwwwardsProvider(SourceProvider):
    slug = "awwwards"
    source_url = "https://www.awwwards.com/websites/"

    def discover(self) -> list[DiscoveredWebsiteRecord]:
        page = self.fetch_catalog()
        records: list[DiscoveredWebsiteRecord] = []
        seen_details: set[str] = set()

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
                    metadata={"detailUrl": detail_url},
                )
            )

        return records
