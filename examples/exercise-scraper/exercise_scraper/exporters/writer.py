from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from exercise_scraper.models import CrawlManifest, Exercise, SourcePage


def slugify(value: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", value.lower(), flags=re.UNICODE)
    slug = re.sub(r"[\s_-]+", "-", slug).strip("-")
    return slug or "exercises"


def make_output_dir(base: Path, query: str) -> Path:
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return base / f"{slugify(query)}_{date}"


def split_items(raw_items: list[dict]) -> tuple[list[Exercise], list[SourcePage]]:
    exercises: list[Exercise] = []
    pages: list[SourcePage] = []

    for item in raw_items:
        if item.get("_page_meta"):
            pages.append(
                SourcePage(
                    url=item["url"],
                    title=item.get("title", ""),
                    exercise_count=item.get("exercise_count", 0),
                    language="unknown",
                    status=item.get("status"),
                )
            )
            continue

        extracted_at = item.get("extracted_at")
        if isinstance(extracted_at, str):
            item = {**item, "extracted_at": datetime.fromisoformat(extracted_at)}

        exercises.append(Exercise(**item))

    return exercises, pages


def deduplicate_exercises(exercises: list[Exercise]) -> list[Exercise]:
    seen: set[str] = set()
    unique: list[Exercise] = []
    for exercise in exercises:
        if exercise.id in seen:
            continue
        seen.add(exercise.id)
        unique.append(exercise)
    return unique


def write_corpus_outputs(
    output_dir: Path,
    validation: "ValidationPipelineResult",
    manifest: CrawlManifest,
    *,
    search_urls: list[dict[str, str]] | None = None,
    save_rejected: bool = True,
    top_n: int = 3,
    save_html: bool = False,
) -> None:
    from exercise_scraper.validation.pipeline import ValidationPipelineResult

    output_dir.mkdir(parents=True, exist_ok=True)
    pages_dir = output_dir / "pages"
    pages_dir.mkdir(exist_ok=True)

    top = deduplicate_exercises(validation.top)
    passed = deduplicate_exercises(validation.passed)
    rejected = deduplicate_exercises(validation.rejected)

    manifest.exercises_total = len(top)
    manifest.exercises_pl = len([ex for ex in top if ex.language == "pl"])
    manifest.exercises_en = len([ex for ex in top if ex.language == "en"])
    manifest.exercises_unknown = len([ex for ex in top if ex.language == "unknown"])
    manifest.finished_at = datetime.now(timezone.utc)

    top_filename = f"exercises_top{top_n}.json"
    _write_json(output_dir / top_filename, [ex.to_dict() for ex in top])
    _write_json(output_dir / "exercises.json", [ex.to_dict() for ex in top])
    _write_json(output_dir / "exercises_validated.json", [ex.to_dict() for ex in passed])
    if save_rejected:
        _write_json(output_dir / "exercises_rejected.json", [ex.to_dict() for ex in rejected])
    _write_json(
        output_dir / "validation_report.json",
        validation.to_report(top_n=top_n),
    )
    if search_urls is not None:
        _write_json(output_dir / "sources.json", search_urls)
    _write_json(output_dir / "manifest.json", manifest.to_dict())

    for index, exercise in enumerate(top, start=1):
        _append_markdown_page(pages_dir, index, exercise)

    _write_report(output_dir / "report.txt", manifest, top, extra_lines=_validation_report_lines(validation, top_n))

    if save_html:
        (output_dir / "raw_html").mkdir(exist_ok=True)


def _validation_report_lines(validation: "ValidationPipelineResult", top_n: int) -> list[str]:
    return [
        "",
        "Validation:",
        f"  Raw extracted: {validation.raw_total}",
        f"  Passed: {len(validation.passed)}",
        f"  Rejected: {len(validation.rejected)}",
        f"  Top {top_n} saved: {len(validation.top)}",
    ]


def write_outputs(
    output_dir: Path,
    exercises: list[Exercise],
    manifest: CrawlManifest,
    *,
    save_html: bool = False,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    pages_dir = output_dir / "pages"
    pages_dir.mkdir(exist_ok=True)

    exercises = deduplicate_exercises(exercises)
    exercises_pl = [ex for ex in exercises if ex.language == "pl"]
    exercises_en = [ex for ex in exercises if ex.language == "en"]
    exercises_unknown = [ex for ex in exercises if ex.language == "unknown"]

    manifest.exercises_total = len(exercises)
    manifest.exercises_pl = len(exercises_pl)
    manifest.exercises_en = len(exercises_en)
    manifest.exercises_unknown = len(exercises_unknown)
    manifest.finished_at = datetime.now(timezone.utc)

    _write_json(output_dir / "exercises.json", [ex.to_dict() for ex in exercises])
    _write_json(output_dir / "exercises_pl.json", [ex.to_dict() for ex in exercises_pl])
    _write_json(output_dir / "exercises_en.json", [ex.to_dict() for ex in exercises_en])
    _write_json(output_dir / "manifest.json", manifest.to_dict())

    for index, exercise in enumerate(exercises, start=1):
        _append_markdown_page(pages_dir, index, exercise)

    _write_report(output_dir / "report.txt", manifest, exercises, extra_lines=None)

    if save_html:
        (output_dir / "raw_html").mkdir(exist_ok=True)


def _write_json(path: Path, payload: list | dict) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _append_markdown_page(pages_dir: Path, index: int, exercise: Exercise) -> None:
    host = re.sub(r"^www\.", "", exercise.source_url.split("/")[2])
    filename = f"{index:03d}_{slugify(host)}.md"
    path = pages_dir / filename

    if path.exists():
        content = path.read_text(encoding="utf-8")
    else:
        content = f"# {exercise.source_title or host}\n\nSource: {exercise.source_url}\n\n"

    content += (
        f"\n## Exercise {index}\n\n"
        f"{exercise.text}\n\n"
        f"- Language: {exercise.language}\n"
        f"- Type: {exercise.exercise_type}\n"
        f"- Confidence: {exercise.confidence:.2f}\n"
    )
    if exercise.answers:
        content += f"- Answers: {exercise.answers}\n"
    path.write_text(content, encoding="utf-8")


def _write_report(
    path: Path,
    manifest: CrawlManifest,
    exercises: list[Exercise],
    extra_lines: list[str] | None = None,
) -> None:
    lines = [
        "Exercise Scraper Report",
        "=======================",
        f"Query: {manifest.query}",
        f"Language mode: {manifest.lang_mode}",
        f"URLs found: {manifest.urls_found}",
        f"URLs scraped: {manifest.urls_scraped}",
        f"URLs failed: {manifest.urls_failed}",
        f"Exercises total: {manifest.exercises_total}",
        f"  PL: {manifest.exercises_pl}",
        f"  EN: {manifest.exercises_en}",
        f"  Unknown: {manifest.exercises_unknown}",
        "",
        "Top sources:",
    ]

    source_counts: dict[str, int] = {}
    for exercise in exercises:
        host = exercise.source_url.split("/")[2]
        source_counts[host] = source_counts.get(host, 0) + 1

    for host, count in sorted(source_counts.items(), key=lambda item: item[1], reverse=True)[:10]:
        lines.append(f"  - {host}: {count}")

    if extra_lines:
        lines.extend(extra_lines)

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
