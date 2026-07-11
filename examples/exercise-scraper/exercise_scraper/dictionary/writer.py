from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from exercise_scraper.dictionary.models import VocabularyExercise, WordEntry


def dictionary_output_dir(base: Path, track_id: str) -> Path:
    return base / "grammar-corpus" / "dictionary" / track_id


def write_dictionary_outputs(
    output_dir: Path,
    *,
    track_id: str,
    level: str,
    words: list[WordEntry],
    all_exercises: list[VocabularyExercise],
    top_exercises: list[VocabularyExercise],
    sources: list[dict[str, str]],
    top_n: int,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    words_payload = [{"en": w.en, "pl": w.pl, "pos": w.pos} for w in words]
    _write_json(output_dir / "words.json", words_payload)
    _write_json(output_dir / "exercises_raw.json", [ex.to_dict() for ex in all_exercises])
    _write_json(output_dir / "exercises_validated.json", [ex.to_dict() for ex in all_exercises if ex.validation_score >= 0.45])
    _write_json(output_dir / f"exercises_top{top_n}.json", [ex.to_dict() for ex in top_exercises])
    _write_json(output_dir / "exercises.json", [ex.to_dict() for ex in top_exercises])
    _write_json(output_dir / "sources.json", sources)
    _write_json(
        output_dir / "manifest.json",
        {
            "track_id": track_id,
            "level": level,
            "words_total": len(words),
            "exercises_raw": len(all_exercises),
            "exercises_top": len(top_exercises),
            "finished_at": datetime.now(timezone.utc).isoformat(),
        },
    )

    report_lines = [
        "Dictionary Scraper Report",
        "=======================",
        f"Track: {track_id}",
        f"Level: {level}",
        f"Words in list: {len(words)}",
        f"Exercises raw: {len(all_exercises)}",
        f"Top {top_n} saved: {len(top_exercises)}",
        "",
        "Top words covered:",
    ]
    for exercise in top_exercises:
        report_lines.append(f"  - {exercise.matched_word} → {exercise.matched_translation}")

    (output_dir / "report.txt").write_text("\n".join(report_lines) + "\n", encoding="utf-8")


def _write_json(path: Path, payload: list | dict) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
