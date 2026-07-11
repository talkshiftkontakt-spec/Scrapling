from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Literal

from exercise_scraper.config import Settings
from exercise_scraper.crawl.spider import ExerciseSpider
from exercise_scraper.corpus.index import CorpusIndex
from exercise_scraper.corpus.paths import resolve_output_dir
from exercise_scraper.drive.sync import drive_configured, upload_topic_folder
from exercise_scraper.exporters.writer import split_items, write_corpus_outputs
from exercise_scraper.models import CrawlManifest, Exercise
from exercise_scraper.queries import build_queries
from exercise_scraper.search import collect_urls, get_provider
from exercise_scraper.taxonomy import GrammarTopic, load_grammar_taxonomy
from exercise_scraper.validation.pipeline import ValidationPipelineResult, run_validation_pipeline

LangMode = Literal["pl", "en", "both"]
ProviderMode = Literal["duckduckgo", "serpapi"]

ProgressCallback = Callable[[str, dict], None]


@dataclass
class ScrapeRequest:
    topic: str
    lang: LangMode = "both"
    max_pages: int | None = None
    delay: float | None = None
    min_confidence: float | None = None
    provider: ProviderMode = "duckduckgo"
    topic_en: str | None = None
    topic_pl: str | None = None
    output_base: Path = Path("output")
    dry_run: bool = False
    top_exercises: int = 3
    topic_id: str | None = None
    use_corpus_layout: bool = False
    validator_names: list[str] = field(default_factory=list)
    save_rejected: bool = True
    sync_drive: bool = False


@dataclass
class ScrapeResult:
    manifest: CrawlManifest
    exercises: list[Exercise]
    output_dir: Path
    search_urls: list[dict[str, str]]
    elapsed_seconds: float
    requests_count: int
    validation: ValidationPipelineResult | None = None
    drive_sync: dict | None = None


def _resolve_topic(request: ScrapeRequest) -> GrammarTopic | None:
    if not request.topic_id:
        return None
    return load_grammar_taxonomy().get(request.topic_id)


def run_scrape(
    request: ScrapeRequest,
    *,
    settings: Settings | None = None,
    on_progress: ProgressCallback | None = None,
) -> ScrapeResult:
    settings = settings or Settings.from_env()
    max_pages = request.max_pages or settings.max_pages
    delay = request.delay if request.delay is not None else settings.download_delay
    min_confidence = (
        request.min_confidence if request.min_confidence is not None else settings.min_confidence
    )

    if request.provider == "serpapi" and not settings.serpapi_key:
        raise ValueError("SERPAPI_KEY is required when provider is serpapi")

    topic_entry = _resolve_topic(request)
    validator_names = request.validator_names or (topic_entry.validators if topic_entry else [])

    def emit(phase: str, payload: dict | None = None) -> None:
        if on_progress:
            on_progress(phase, payload or {})

    query_pairs = build_queries(
        request.topic,
        request.lang,
        topic_en=request.topic_en,
        topic_pl=request.topic_pl,
        limit_per_lang=settings.queries_per_lang,
    )
    queries_used = [query for query, _ in query_pairs]

    emit("searching", {"topic": request.topic, "lang": request.lang, "queries": queries_used})

    search_provider = get_provider(request.provider, settings)
    search_results = collect_urls(
        search_provider,
        query_pairs,
        max_pages=max_pages,
        results_per_query=settings.results_per_query,
    )

    if topic_entry:
        seen = {result.url for result in search_results}
        for url in topic_entry.seed_urls:
            if url not in seen:
                from exercise_scraper.models import SearchResult

                search_results.append(
                    SearchResult(url=url, title=topic_entry.primary_en, query="seed", snippet="")
                )
                seen.add(url)

    if not search_results:
        raise ValueError("No URLs found for this topic. Try another phrase or provider.")

    search_urls = [
        {"url": result.url, "title": result.title, "query": result.query}
        for result in search_results
    ]
    emit("urls_found", {"count": len(search_results), "urls": search_urls})

    if request.dry_run:
        manifest = CrawlManifest(
            query=request.topic,
            lang_mode=request.lang,
            output_dir="",
            urls_found=len(search_results),
            queries_used=queries_used,
        )
        return ScrapeResult(
            manifest=manifest,
            exercises=[],
            output_dir=request.output_base,
            search_urls=search_urls,
            elapsed_seconds=0.0,
            requests_count=0,
        )

    output_dir = resolve_output_dir(
        request.output_base,
        topic=topic_entry,
        query=request.topic,
        use_corpus_layout=request.use_corpus_layout or request.topic_id is not None,
    )
    manifest = CrawlManifest(
        query=request.topic,
        lang_mode=request.lang,
        output_dir=str(output_dir),
        urls_found=len(search_results),
        queries_used=queries_used,
    )

    urls = [result.url for result in search_results]
    emit("crawling", {"count": len(urls)})

    spider = ExerciseSpider(
        urls=urls,
        topic=request.topic,
        min_confidence=min_confidence,
        download_delay=delay,
    )
    crawl_result = spider.start()

    exercises, pages = split_items(list(crawl_result.items))
    emit("validating", {"raw_count": len(exercises)})

    validation = run_validation_pipeline(
        exercises,
        topic_id=request.topic_id,
        validator_names=validator_names,
        top_n=request.top_exercises,
    )

    if request.topic_id:
        index = CorpusIndex(request.output_base / "grammar-corpus" / "manifests" / "corpus_index.db")
        deduped_top: list = []
        for exercise in validation.top:
            if index.has_seen(kind="grammar", topic_key=request.topic_id, text=exercise.text):
                continue
            deduped_top.append(exercise)
            index.register(
                kind="grammar",
                topic_key=request.topic_id,
                text=exercise.text,
                source_url=exercise.source_url,
                validation_score=exercise.validation_score,
            )
        if deduped_top:
            validation.top = deduped_top
            validation.ranked = deduped_top

    manifest.urls_scraped = len(pages)
    manifest.urls_failed = max(0, len(urls) - len(pages))
    manifest.sources = [
        {"url": page.url, "title": page.title, "count": page.exercise_count}
        for page in pages
    ]

    write_corpus_outputs(
        output_dir,
        validation,
        manifest,
        search_urls=search_urls,
        save_rejected=request.save_rejected,
        top_n=request.top_exercises,
    )

    drive_sync: dict | None = None
    if request.sync_drive and topic_entry and drive_configured():
        emit("drive_sync", {"topic_id": topic_entry.id})
        drive_sync = upload_topic_folder(
            output_dir,
            topic_id=topic_entry.id,
            level=topic_entry.level,
        )

    emit(
        "completed",
        {
            "exercises_total": manifest.exercises_total,
            "exercises_pl": manifest.exercises_pl,
            "exercises_en": manifest.exercises_en,
            "output_dir": str(output_dir),
            "top_exercises": request.top_exercises,
            "passed": len(validation.passed),
            "rejected": len(validation.rejected),
        },
    )

    return ScrapeResult(
        manifest=manifest,
        exercises=validation.top,
        output_dir=output_dir,
        search_urls=search_urls,
        elapsed_seconds=crawl_result.stats.elapsed_seconds,
        requests_count=crawl_result.stats.requests_count,
        validation=validation,
        drive_sync=drive_sync,
    )
