from __future__ import annotations

from pathlib import Path
from typing import Literal, Optional

import typer

from exercise_scraper.config import Settings
from exercise_scraper.crawl.spider import ExerciseSpider
from exercise_scraper.models import CrawlManifest
from exercise_scraper.exporters.writer import make_output_dir, split_items, write_outputs
from exercise_scraper.queries import build_queries
from exercise_scraper.search import collect_urls, get_provider

app = typer.Typer(
    name="exercise-scraper",
    help="Search and scrape grammar exercises from the web (Polish + English).",
    add_completion=False,
)

LangMode = Literal["pl", "en", "both"]
ProviderMode = Literal["duckduckgo", "serpapi"]


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
    dry_run: bool = typer.Option(False, "--dry-run", help="Only list URLs, do not scrape"),
    save_html: bool = typer.Option(False, "--save-html", help="Reserve raw_html/ directory"),
    verbose: bool = typer.Option(False, "--verbose", help="Show detailed progress"),
) -> None:
    """Search the web for exercises and save extracted tasks to disk."""
    settings = Settings.from_env()
    max_pages = max_pages or settings.max_pages
    delay = delay if delay is not None else settings.download_delay
    min_confidence = min_confidence if min_confidence is not None else settings.min_confidence

    if provider == "serpapi" and not settings.serpapi_key:
        typer.secho("SERPAPI_KEY is not set. Use --provider duckduckgo or export SERPAPI_KEY.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    query_pairs = build_queries(
        topic,
        lang,
        topic_en=topic_en,
        topic_pl=topic_pl,
        limit_per_lang=settings.queries_per_lang,
    )
    queries_used = [query for query, _ in query_pairs]

    typer.echo(f'🔍 Wyszukiwanie / Searching: "{topic}" (lang={lang})')
    if verbose:
        for query in queries_used:
            typer.echo(f"   • {query}")

    search_provider = get_provider(provider, settings)
    search_results = collect_urls(
        search_provider,
        query_pairs,
        max_pages=max_pages,
        results_per_query=settings.results_per_query,
    )

    if not search_results:
        typer.secho("No URLs found. Try a different topic or provider.", fg=typer.colors.YELLOW)
        raise typer.Exit(code=1)

    typer.echo(f"   Found {len(search_results)} unique URLs")

    if dry_run:
        for index, result in enumerate(search_results, start=1):
            typer.echo(f"{index:>3}. {result.title}\n     {result.url}")
        raise typer.Exit()

    output_dir = make_output_dir(output, topic)
    manifest = CrawlManifest(
        query=topic,
        lang_mode=lang,
        output_dir=str(output_dir),
        urls_found=len(search_results),
        queries_used=queries_used,
    )

    urls = [result.url for result in search_results]
    spider = ExerciseSpider(
        urls=urls,
        topic=topic,
        min_confidence=min_confidence,
        download_delay=delay,
    )

    typer.echo(f"📥 Crawling {len(urls)} pages (delay={delay}s)...")
    result = spider.start()

    exercises, pages = split_items(list(result.items))
    manifest.urls_scraped = len(pages)
    manifest.urls_failed = max(0, len(urls) - len(pages))
    manifest.sources = [
        {
            "url": page.url,
            "title": page.title,
            "count": page.exercise_count,
        }
        for page in pages
    ]

    write_outputs(output_dir, exercises, manifest, save_html=save_html)

    typer.secho("\n✅ Done / Gotowe", fg=typer.colors.GREEN, bold=True)
    typer.echo(f"   Output: {output_dir}")
    typer.echo(
        f"   Exercises: {manifest.exercises_total} "
        f"(PL: {manifest.exercises_pl}, EN: {manifest.exercises_en}, unknown: {manifest.exercises_unknown})"
    )
    typer.echo(f"   Requests: {result.stats.requests_count}, time: {result.stats.elapsed_seconds:.1f}s")


if __name__ == "__main__":
    app()
