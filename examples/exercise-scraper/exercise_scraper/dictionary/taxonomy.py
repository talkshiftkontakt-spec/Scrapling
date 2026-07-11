from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from exercise_scraper.config_paths import CONFIG_DIR
from exercise_scraper.dictionary.models import WordEntry


@dataclass
class DictionaryTrack:
    id: str
    level: str
    language_pair: list[str]
    source: str
    wordlist: str
    description: str
    search_queries: dict[str, list[str]] = field(default_factory=dict)
    allowed_domains: list[str] = field(default_factory=list)

    @property
    def primary_lang(self) -> str:
        return self.language_pair[0] if self.language_pair else "en"


def load_dictionary_tracks(path: Path | None = None) -> list[DictionaryTrack]:
    config_path = path or (CONFIG_DIR / "dictionary_taxonomy.yaml")
    raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    tracks: list[DictionaryTrack] = []
    for item in raw.get("tracks", []):
        tracks.append(
            DictionaryTrack(
                id=item["id"],
                level=item["level"],
                language_pair=list(item.get("language_pair", ["en", "pl"])),
                source=item.get("source", "open_wordlist"),
                wordlist=item.get("wordlist", ""),
                description=item.get("description", ""),
                search_queries=dict(item.get("search_queries", {})),
                allowed_domains=list(item.get("allowed_domains", [])),
            )
        )
    return tracks


def get_dictionary_track(track_id: str) -> DictionaryTrack | None:
    for track in load_dictionary_tracks():
        if track.id == track_id:
            return track
    return None


def load_wordlist(relative_path: str) -> list[WordEntry]:
    path = CONFIG_DIR / relative_path
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return [
        WordEntry(en=item["en"], pl=item["pl"], pos=item.get("pos", "unknown"))
        for item in raw.get("words", [])
    ]
