from __future__ import annotations

from pathlib import Path
from typing import Literal, Optional

import typer

from exercise_scraper.config import Settings
from exercise_scraper.corpus.orchestrator import run_corpus_batch, run_corpus_topic
from exercise_scraper.dictionary.service import DictionaryRunRequest, run_dictionary_track
from exercise_scraper.dictionary.taxonomy import load_dictionary_tracks
from exercise_scraper.service import ScrapeRequest, run_scrape
from exercise_scraper.taxonomy import load_grammar_taxonomy

app = typer.Typer(
    name="exercise-scraper",
    help="Search and scrape grammar exercises from the web (Polish + English).",
    add_completion=False,
)

corpus_app = typer.Typer(help="Grammar corpus builder (taxonomy-driven).")
dictionary_app = typer.Typer(help="Vocabulary / słówka track.")
app.add_typer(corpus_app, name="corpus")
app.add_typer(dictionary_app, name="dictionary")

LangMode = Literal["pl", "en", "both"]
ProviderMode = Literal["duckduckgo", "serpapi"]


def _base_request(
    *,
    lang: LangMode,
    max_pages: Optional[int],
    output: Path,
    delay: Optional[float],
    min_confidence: Optional[float],
    provider: ProviderMode,
    top_n: int,
    sync_drive: bool,
) -> ScrapeRequest:
    settings = Settings.from_env()
    return ScrapeRequest(
        topic="",
        lang=lang,
        max_pages=max_pages or settings.max_pages,
        delay=delay if delay is not None else settings.download_delay,
        min_confidence=min_confidence if min_confidence is not None else settings.min_confidence,
        provider=provider,
        output_base=output,
        top_exercises=top_n,
        sync_drive=sync_drive,
    )


@app.command()
def scrape(
    topic: str = typer.Argument(..., help='Topic phrase, e.g. "Past Simple"'),
    lang: LangMode = typer.Option("both", "--lang", help="Language mode: pl, en, or both"),
    max_pages: Optional[int] = typer.Option(None, "--max-pages", help="Maximum URLs to scrape"),
    output: Path = typer.Option(Path("output"), "--output", help="Base output directory"),
    delay: Optional[float] = typer.Option(None, "--delay", help="Delay between requests (seconds)"),
    min_confidence: Optional[float] = typer.Option(
        None, "--min-confidence", help="Minimum extraction confidence (0.0–1.0)"
    ),
    provider: ProviderMode = typer.Option(
        "duckduckgo", "--provider", help="Search provider: duckduckgo or serpapi"
    ),
    topic_en: Optional[str] = typer.Option(None, "--topic-en", help="Override English search phrase"),
    topic_pl: Optional[str] = typer.Option(None, "--topic-pl", help="Override Polish search phrase"),
    topic_id: Optional[str] = typer.Option(
        None, "--topic-id", help="Grammar taxonomy id (enables topic validators + corpus layout)"
    ),
    top_n: int = typer.Option(3, "--top-n", min=1, max=100, help="Keep top N validated exercises"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Only list URLs, do not scrape"),
    save_html: bool = typer.Option(False, "--save-html", help="Reserve raw_html/ directory"),
    sync_drive: bool = typer.Option(False, "--sync-drive", help="Upload to Google Drive after scrape"),
    verbose: bool = typer.Option(False, "--verbose", help="Show detailed progress"),
) -> None:
    """Search the web for exercises and save extracted tasks to disk."""
    settings = Settings.from_env()
    if provider == "serpapi" and not settings.serpapi_key:
        typer.secho("SERPAPI_KEY is not set. Use --provider duckduckgo or export SERPAPI_KEY.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    request = ScrapeRequest(
        topic=topic,
        lang=lang,
        max_pages=max_pages or settings.max_pages,
        delay=delay if delay is not None else settings.download_delay,
        min_confidence=min_confidence if min_confidence is not None else settings.min_confidence,
        provider=provider,
        topic_en=topic_en,
        topic_pl=topic_pl,
        output_base=output,
        dry_run=dry_run,
        top_exercises=top_n,
        topic_id=topic_id,
        use_corpus_layout=bool(topic_id),
        sync_drive=sync_drive,
    )

    if topic_id:
        taxonomy = load_grammar_taxonomy()
        entry = taxonomy.get(topic_id)
        if entry is None:
            typer.secho(f"Unknown topic_id: {topic_id}", fg=typer.colors.RED)
            raise typer.Exit(code=1)
        request.validator_names = entry.validators
        request.topic_en = entry.primary_en
        request.topic_pl = entry.primary_pl

    def on_progress(phase: str, payload: dict) -> None:
        if verbose:
            typer.echo(f"[{phase}] {payload}")

    typer.echo(f'🔍 Searching: "{topic}" (lang={lang}, top_n={top_n})')
    result = run_scrape(request, settings=settings, on_progress=on_progress if verbose else None)

    if dry_run:
        for index, item in enumerate(result.search_urls, start=1):
            typer.echo(f"{index:>3}. {item['title']}\n     {item['url']}")
        raise typer.Exit()

    typer.secho("\n✅ Done", fg=typer.colors.GREEN, bold=True)
    typer.echo(f"   Output: {result.output_dir}")
    if result.validation:
        typer.echo(
            f"   Validation: {result.validation.raw_total} raw → "
            f"{len(result.validation.passed)} passed → top {len(result.exercises)}"
        )
    typer.echo(f"   Requests: {result.requests_count}, time: {result.elapsed_seconds:.1f}s")
    if result.drive_sync:
        typer.echo(f"   Drive: {result.drive_sync.get('uploaded', False)}")


@corpus_app.command("topics")
def corpus_topics(category: Optional[str] = typer.Option(None, "--category", help="tenses|structures")) -> None:
    """List grammar topics from taxonomy."""
    taxonomy = load_grammar_taxonomy()
    topics = taxonomy.topics
    if category:
        topics = [topic for topic in topics if topic.grammar_category == category]
    for topic in topics:
        typer.echo(f"{topic.grammar_category:10} {topic.level:3}  {topic.id:28}  {topic.primary_en}")


@corpus_app.command("run-topic")
def corpus_run_topic(
    topic_id: str = typer.Argument(..., help="Taxonomy topic id, e.g. past-simple"),
    lang: LangMode = typer.Option("both", "--lang"),
    max_pages: Optional[int] = typer.Option(None, "--max-pages"),
    output: Path = typer.Option(Path("output"), "--output"),
    delay: Optional[float] = typer.Option(None, "--delay"),
    min_confidence: Optional[float] = typer.Option(None, "--min-confidence"),
    provider: ProviderMode = typer.Option("duckduckgo", "--provider"),
    top_n: int = typer.Option(3, "--top-n", min=1, max=100),
    sync_drive: bool = typer.Option(False, "--sync-drive"),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """Run full corpus pipeline for one taxonomy topic."""
    request = _base_request(
        lang=lang,
        max_pages=max_pages,
        output=output,
        delay=delay,
        min_confidence=min_confidence,
        provider=provider,
        top_n=top_n,
        sync_drive=sync_drive,
    )
    request.dry_run = dry_run
    run = run_corpus_topic(topic_id, request)
    if not run.success:
        typer.secho(f"Failed: {run.error}", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    typer.secho(f"✅ {topic_id} → {run.scrape_result.output_dir if run.scrape_result else ''}", fg=typer.colors.GREEN)


@corpus_app.command("run-all")
def corpus_run_all(
    lang: LangMode = typer.Option("both", "--lang"),
    max_pages: Optional[int] = typer.Option(5, "--max-pages", help="URLs per topic (keep low for batch)"),
    output: Path = typer.Option(Path("output"), "--output"),
    top_n: int = typer.Option(3, "--top-n", min=1, max=100),
    provider: ProviderMode = typer.Option("duckduckgo", "--provider"),
    sync_drive: bool = typer.Option(False, "--sync-drive"),
    limit: Optional[int] = typer.Option(None, "--limit", help="Max topics to run"),
) -> None:
    """Run corpus pipeline for all taxonomy topics."""
    taxonomy = load_grammar_taxonomy()
    topic_ids = taxonomy.ids()[: limit or len(taxonomy.topics)]
    request = _base_request(
        lang=lang,
        max_pages=max_pages,
        output=output,
        delay=None,
        min_confidence=None,
        provider=provider,
        top_n=top_n,
        sync_drive=sync_drive,
    )
    batch = run_corpus_batch(request, topic_ids=topic_ids)
    typer.echo(f"Batch: {batch.completed}/{batch.started} ok, {batch.failed} failed")


@dictionary_app.command("tracks")
def dictionary_tracks() -> None:
    """List vocabulary tracks."""
    for track in load_dictionary_tracks():
        typer.echo(f"{track.level:3}  {track.id:12}  {track.description}")


@dictionary_app.command("run-track")
def dictionary_run_track(
    track_id: str = typer.Argument(..., help="e.g. en-pl-a1"),
    max_pages: Optional[int] = typer.Option(12, "--max-pages"),
    output: Path = typer.Option(Path("output"), "--output"),
    provider: ProviderMode = typer.Option("duckduckgo", "--provider"),
    top_n: int = typer.Option(5, "--top-n", min=1, max=50),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """Scrape vocabulary exercises for a dictionary track."""
    request = DictionaryRunRequest(
        track_id=track_id,
        max_pages=max_pages,
        provider=provider,
        output_base=output,
        top_exercises=top_n,
        dry_run=dry_run,
    )
    result = run_dictionary_track(request)
    typer.secho(f"✅ {track_id} → {result.output_dir}", fg=typer.colors.GREEN)
    typer.echo(f"   Words: {result.words_count}, exercises: {len(result.exercises_top)}")


if __name__ == "__main__":
    app()
