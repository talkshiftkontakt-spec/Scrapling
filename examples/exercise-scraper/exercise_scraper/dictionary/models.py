from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal

VocabCategory = Literal["word", "phrase", "translation"]


@dataclass
class WordEntry:
    en: str
    pl: str
    pos: str = "unknown"


@dataclass
class VocabularyExercise:
    text: str
    track_id: str
    level: str
    matched_word: str
    matched_translation: str
    source_url: str
    source_title: str = ""
    language: str = "unknown"
    exercise_type: str = "translation"
    confidence: float = 0.0
    validation_score: float = 0.0
    validation_reasons: list[str] = field(default_factory=list)
    id: str = ""
    extracted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
            "track_id": self.track_id,
            "level": self.level,
            "matched_word": self.matched_word,
            "matched_translation": self.matched_translation,
            "source_url": self.source_url,
            "source_title": self.source_title,
            "language": self.language,
            "exercise_type": self.exercise_type,
            "confidence": self.confidence,
            "validation_score": self.validation_score,
            "validation_reasons": self.validation_reasons,
            "extracted_at": self.extracted_at.isoformat(),
        }
