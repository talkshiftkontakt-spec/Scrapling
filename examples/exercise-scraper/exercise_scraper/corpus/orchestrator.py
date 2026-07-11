from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from exercise_scraper.models import SearchResult
from exercise_scraper.search import collect_urls, get_provider
from exercise_scraper.service import ScrapeRequest, ScrapeResult, run_scrape
from exercise_scraper.taxonomy import GrammarTaxonomy, GrammarTopic, load_grammar_taxonomy

ProgressCallback = Callable[[str, dict], None]


@dataclass
class CorpusRunResult:
    topic_id: str
    topic_level: str
    success: bool
    error: str | None = None
    scrape_result: ScrapeResult | None = None


@dataclass
class CorpusBatchResult:
    started: int = 0
    completed: int = 0
    failed: int = 0
    runs: list[CorpusRunResult] = field(default_factory=list)


def build_topic_search_results(
    topic: GrammarTopic,
    *,
    provider: str,
    settings,
    max_pages: int,
    lang: str = "both",
) -> list[SearchResult]:
    from exercise_scraper.queries import build_queries

    search_provider = get_provider(provider, settings)  # type: ignore[arg-type]
    query_pairs = build_queries(
        topic.primary_en,
        lang,  # type: ignore[arg-type]
        topic_en=topic.primary_en,
        topic_pl=topic.primary_pl,
    )
    results = collect_urls(
        search_provider,
        query_pairs,
        max_pages=max_pages,
        results_per_query=settings.results_per_query,
    )

    seen = {result.url for result in results}
    for url in topic.seed_urls:
        if url not in seen:
            results.append(SearchResult(url=url, title=topic.primary_en, query="seed", snippet=""))
            seen.add(url)
    return results


def run_corpus_topic(
    topic_id: str,
    request: ScrapeRequest,
    *,
    taxonomy: GrammarTaxonomy | None = None,
    on_progress: ProgressCallback | None = None,
) -> CorpusRunResult:
    taxonomy = taxonomy or load_grammar_taxonomy()
    topic = taxonomy.get(topic_id)
    if topic is None:
        return CorpusRunResult(topic_id=topic_id, topic_level="", success=False, error="Unknown topic_id")

    enriched = ScrapeRequest(
        topic=topic.primary_en,
        lang=request.lang,
        max_pages=request.max_pages,
        delay=request.delay,
        min_confidence=request.min_confidence,
        provider=request.provider,
        topic_en=topic.primary_en,
        topic_pl=topic.primary_pl,
        output_base=request.output_base,
        dry_run=request.dry_run,
        top_exercises=request.top_exercises,
        topic_id=topic.id,
        use_corpus_layout=True,
        validator_names=topic.validators,
        save_rejected=True,
    )

    try:
        result = run_scrape(enriched, on_progress=on_progress)
        return CorpusRunResult(
            topic_id=topic.id,
            topic_level=topic.level,
            success=True,
            scrape_result=result,
        )
    except Exception as exc:
        return CorpusRunResult(
            topic_id=topic.id,
            topic_level=topic.level,
            success=False,
            error=str(exc),
        )


def run_corpus_batch(
    request: ScrapeRequest,
    *,
    topic_ids: list[str] | None = None,
    on_progress: ProgressCallback | None = None,
) -> CorpusBatchResult:
    taxonomy = load_grammar_taxonomy()
    ids = topic_ids or taxonomy.ids()
    batch = CorpusBatchResult()

    for topic_id in ids:
        batch.started += 1
        if on_progress:
            on_progress("batch_topic_start", {"topic_id": topic_id})
        run = run_corpus_topic(topic_id, request, taxonomy=taxonomy, on_progress=on_progress)
        batch.runs.append(run)
        if run.success:
            batch.completed += 1
        else:
            batch.failed += 1
        if on_progress:
            on_progress(
                "batch_topic_done",
                {"topic_id": topic_id, "success": run.success, "error": run.error},
            )

    return batch
