from __future__ import annotations

from abc import ABC, abstractmethod
from urllib.parse import urljoin

from scrapling.fetchers import Fetcher

from ingestion.scrapling.contracts import DiscoveredWebsiteRecord


class SourceProvider(ABC):
    slug: str
    source_url: str

    def fetch_catalog(self):
        return Fetcher.get(self.source_url, timeout=30000)

    @abstractmethod
    def discover(self) -> list[DiscoveredWebsiteRecord]:
        raise NotImplementedError

    def normalize_url(self, url: str) -> str:
        return urljoin(self.source_url, url)
