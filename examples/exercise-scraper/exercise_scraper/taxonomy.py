from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from exercise_scraper.config_paths import CONFIG_DIR


@dataclass
class GrammarTopic:
    id: str
    level: str
    en: list[str]
    pl: list[str]
    validators: list[str] = field(default_factory=list)
    exercise_types: list[str] = field(default_factory=list)
    seed_urls: list[str] = field(default_factory=list)

    @property
    def primary_en(self) -> str:
        return self.en[0] if self.en else self.id

    @property
    def primary_pl(self) -> str:
        return self.pl[0] if self.pl else self.id


@dataclass
class GrammarTaxonomy:
    topics: list[GrammarTopic]

    def get(self, topic_id: str) -> GrammarTopic | None:
        for topic in self.topics:
            if topic.id == topic_id:
                return topic
        return None

    def ids(self) -> list[str]:
        return [topic.id for topic in self.topics]


def load_grammar_taxonomy(path: Path | None = None) -> GrammarTaxonomy:
    config_path = path or (CONFIG_DIR / "grammar_taxonomy.yaml")
    raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    topics = [_parse_topic(item) for item in raw.get("topics", [])]
    return GrammarTaxonomy(topics=topics)


def load_dictionary_taxonomy(path: Path | None = None) -> list[dict[str, Any]]:
    config_path = path or (CONFIG_DIR / "dictionary_taxonomy.yaml")
    raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    return list(raw.get("tracks", []))


def _parse_topic(item: dict[str, Any]) -> GrammarTopic:
    return GrammarTopic(
        id=item["id"],
        level=item["level"],
        en=list(item.get("en", [])),
        pl=list(item.get("pl", [])),
        validators=list(item.get("validators", [])),
        exercise_types=list(item.get("exercise_types", [])),
        seed_urls=list(item.get("seed_urls", [])),
    )
