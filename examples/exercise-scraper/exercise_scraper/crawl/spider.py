from __future__ import annotations

from typing import Any, AsyncGenerator

from scrapling.spiders import Response, Spider

from exercise_scraper.extract.domain_rules import load_domain_rules
from exercise_scraper.extract.heuristics import extract_exercises


class ExerciseSpider(Spider):
    name = "exercise_scraper"
    robots_txt_obey = True
    concurrent_requests = 3
    logging_level = 30  # WARNING — quieter CLI output

    def __init__(
        self,
        urls: list[str],
        topic: str,
        *,
        min_confidence: float = 0.4,
        download_delay: float = 1.5,
        crawldir=None,
    ) -> None:
        self.topic = topic
        self.min_confidence = min_confidence
        self.download_delay = download_delay
        self.domain_rules = load_domain_rules()
        self.start_urls = urls
        super().__init__(crawldir=crawldir)

    async def parse(self, response: Response) -> AsyncGenerator[dict[str, Any] | None, None]:
        exercises = extract_exercises(
            response,
            topic=self.topic,
            min_confidence=self.min_confidence,
            domain_rules=self.domain_rules,
        )
        for exercise in exercises:
            yield exercise.to_dict()

        yield {
            "_page_meta": True,
            "url": response.url,
            "title": response.css("title::text").get("") or response.url,
            "status": response.status,
            "exercise_count": len(exercises),
        }
