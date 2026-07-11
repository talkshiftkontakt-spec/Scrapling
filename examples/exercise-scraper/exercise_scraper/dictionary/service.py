from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from exercise_scraper.config import Settings
from exercise_scraper.corpus.index import CorpusIndex
from exercise_scraper.crawl.spider import ExerciseSpider
from exercise_scraper.dictionary.models import VocabularyExercise
from exercise_scraper.dictionary.taxonomy import DictionaryTrack, get_dictionary_track, load_wordlist
from exercise_scraper.dictionary.validate import exercise_to_vocabulary, select_top_vocabulary
from exercise_scraper.dictionary.writer import dictionary_output_dir, write_dictionary_outputs
from exercise_scraper.exporters.writer import split_items
from exercise_scraper.models import SearchResult
from exercise_scraper.search import collect_urls, get_provider

ProgressCallback = Callable[[str, dict], None]


@dataclass
class DictionaryRunRequest:
    track_id: str
    max_pages: int | None = None
    delay: float | None = None
    min_confidence: float | None = None
    provider: str = "duckduckgo"
    output_base: Path = Path("output")
    top_exercises: int = 5
    dry_run: bool = False


@dataclass
class DictionaryRunResult:
    track_id: str
    level: str
    output_dir: Path
    words_count: int
    exercises_raw: int
    exercises_top: list[VocabularyExercise]
    search_urls: list[dict[str, str]]
    elapsed_seconds: float


def _build_dictionary_queries(track: DictionaryTrack) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for lang, queries in track.search_queries.items():
        for query in queries:
            pairs.append((query, lang))
    if not pairs:
        pairs.append((f"{track.level} vocabulary exercises english polish", "both"))
    return pairs


def run_dictionary_track(
    request: DictionaryRunRequest,
    *,
    settings: Settings | None = None,
    on_progress: ProgressCallback | None = None,
) -> DictionaryRunResult:
    settings = settings or Settings.from_env()
    track = get_dictionary_track(request.track_id)
    if track is None:
        raise ValueError(f"Unknown dictionary track: {request.track_id}")

    words = load_wordlist(track.wordlist)
    max_pages = request.max_pages or min(settings.max_pages, 20)
    delay = request.delay if request.delay is not None else settings.download_delay
    min_confidence = (
        request.min_confidence if request.min_confidence is not None else settings.min_confidence
    )

    def emit(phase: str, payload: dict | None = None) -> None:
        if on_progress:
            on_progress(phase, payload or {})

    emit("searching", {"track_id": track.id, "words": len(words)})

    query_pairs = _build_dictionary_queries(track)
    search_provider = get_provider(request.provider, settings)  # type: ignore[arg-type]
    search_results = collect_urls(
        search_provider,
        query_pairs,
        max_pages=max_pages,
        results_per_query=settings.results_per_query,
    )

    search_urls = [
        {"url": result.url, "title": result.title, "query": result.query}
        for result in search_results
    ]

    if request.dry_run:
        return DictionaryRunResult(
            track_id=track.id,
            level=track.level,
            output_dir=request.output_base,
            words_count=len(words),
            exercises_raw=0,
            exercises_top=[],
            search_urls=search_urls,
            elapsed_seconds=0.0,
        )

    if not search_results:
        raise ValueError("No URLs found for this vocabulary track.")

    output_dir = dictionary_output_dir(request.output_base, track.id)
    emit("crawling", {"urls": len(search_results)})

    spider = ExerciseSpider(
        urls=[result.url for result in search_results],
        topic=f"Vocabulary {track.level}",
        min_confidence=min_confidence,
        download_delay=delay,
    )
    crawl_result = spider.start()
    exercises, _pages = split_items(list(crawl_result.items))

    vocab_exercises: list[VocabularyExercise] = []
    for exercise in exercises:
        converted = exercise_to_vocabulary(
            exercise,
            track_id=track.id,
            level=track.level,
            words=words,
        )
        if converted:
            vocab_exercises.append(converted)

    top = select_top_vocabulary(vocab_exercises, limit=request.top_exercises)

    index = CorpusIndex(request.output_base / "grammar-corpus" / "manifests" / "corpus_index.db")
    deduped_top = []
    for item in top:
        if index.has_seen(kind="dictionary", topic_key=track.id, text=item.text):
            continue
        deduped_top.append(item)
        index.register(
            kind="dictionary",
            topic_key=track.id,
            text=item.text,
            source_url=item.source_url,
            validation_score=item.validation_score,
        )
    top = deduped_top or top

    write_dictionary_outputs(
        output_dir,
        track_id=track.id,
        level=track.level,
        words=words,
        all_exercises=vocab_exercises,
        top_exercises=top,
        sources=search_urls,
        top_n=request.top_exercises,
    )

    emit(
        "completed",
        {
            "track_id": track.id,
            "words": len(words),
            "raw": len(vocab_exercises),
            "top": len(top),
            "output_dir": str(output_dir),
        },
    )

    return DictionaryRunResult(
        track_id=track.id,
        level=track.level,
        output_dir=output_dir,
        words_count=len(words),
        exercises_raw=len(vocab_exercises),
        exercises_top=top,
        search_urls=search_urls,
        elapsed_seconds=crawl_result.stats.elapsed_seconds,
    )
