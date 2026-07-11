from __future__ import annotations

from pathlib import Path

from exercise_scraper.exporters.writer import slugify
from exercise_scraper.taxonomy import GrammarTopic


def corpus_root(base: Path) -> Path:
    return base / "grammar-corpus"


def topic_output_dir(base: Path, topic: GrammarTopic) -> Path:
    return corpus_root(base) / "grammar" / topic.level / topic.id


def manifest_dir(base: Path) -> Path:
    return corpus_root(base) / "manifests"


def dictionary_root(base: Path) -> Path:
    return corpus_root(base) / "dictionary"


def legacy_output_dir(base: Path, query: str) -> Path:
    from exercise_scraper.exporters.writer import make_output_dir

    return make_output_dir(base, query)


def resolve_output_dir(
    base: Path,
    *,
    topic: GrammarTopic | None = None,
    query: str,
    use_corpus_layout: bool = False,
) -> Path:
    if use_corpus_layout and topic is not None:
        return topic_output_dir(base, topic)
    return legacy_output_dir(base, query)
