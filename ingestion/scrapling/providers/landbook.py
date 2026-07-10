from __future__ import annotations

from ingestion.scrapling.contracts import DiscoveredWebsiteRecord
from ingestion.scrapling.providers.base import SourceProvider
from ingestion.scrapling.url_resolver import extract_title_from_url, resolve_landbook_visit, strip_tracking_params


class LandbookProvider(SourceProvider):
    slug = "landbook"
    source_url = "https://land-book.com/"

    def discover(self) -> list[DiscoveredWebsiteRecord]:
        page = self.fetch_catalog()
        records: list[DiscoveredWebsiteRecord] = []
        seen_details: set[str] = set()

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

            external_url = resolve_landbook_visit(detail_url)
            if not external_url:
                continue

            records.append(
                DiscoveredWebsiteRecord(
                    website_name=label.split(" - ")[0].strip(),
                    url=strip_tracking_params(external_url),
                    source=self.slug,
                    categories=[],
                    tags=[],
                    provider_reference=detail_url,
                    metadata={"detailUrl": detail_url},
                )
            )

        return records
