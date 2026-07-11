from __future__ import annotations

from abc import ABC, abstractmethod

from exercise_scraper.models import SearchResult


class SearchProvider(ABC):
    @abstractmethod
    def search(self, query: str, *, num: int = 10) -> list[SearchResult]:
        raise NotImplementedError
