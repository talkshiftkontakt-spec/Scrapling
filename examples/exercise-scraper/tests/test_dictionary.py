from __future__ import annotations

from exercise_scraper.dictionary.models import WordEntry
from exercise_scraper.dictionary.taxonomy import get_dictionary_track, load_wordlist
from exercise_scraper.dictionary.validate import (
    exercise_to_vocabulary,
    select_top_vocabulary,
    validate_vocabulary_exercise,
)
from exercise_scraper.models import Exercise


def test_load_a1_wordlist() -> None:
    track = get_dictionary_track("en-pl-a1")
    assert track is not None
    words = load_wordlist(track.wordlist)
    assert len(words) >= 25
    assert isinstance(words[0], WordEntry)


def test_vocabulary_conversion() -> None:
    exercise = Exercise(
        text="1. Translate: water → ___",
        topic="Vocabulary",
        source_url="https://example.test",
        confidence=0.7,
        language="en",
    )
    words = [WordEntry(en="water", pl="woda")]
    vocab = exercise_to_vocabulary(
        exercise,
        track_id="en-pl-a1",
        level="A1",
        words=words,
    )
    assert vocab is not None
    assert vocab.matched_word == "water"


def test_vocabulary_select_top() -> None:
    items = [
        __import__("exercise_scraper.dictionary.models", fromlist=["VocabularyExercise"]).VocabularyExercise(
            text=f"{i}. Match: cat → ___",
            track_id="en-pl-a1",
            level="A1",
            matched_word="cat",
            matched_translation="kot",
            source_url=f"https://a.test/{i}",
            validation_score=0.8 - i * 0.01,
            confidence=0.7,
            id=f"id{i}",
        )
        for i in range(5)
    ]
    top = select_top_vocabulary(items, limit=2)
    assert len(top) == 2


def test_grammar_categories() -> None:
    from exercise_scraper.taxonomy import load_grammar_taxonomy

    taxonomy = load_grammar_taxonomy()
    tenses = [t for t in taxonomy.topics if t.grammar_category == "tenses"]
    structures = [t for t in taxonomy.topics if t.grammar_category == "structures"]
    assert len(tenses) == 8
    assert len(structures) == 12


def test_corpus_index_dedup(tmp_path) -> None:
    from exercise_scraper.corpus.index import CorpusIndex

    index = CorpusIndex(tmp_path / "corpus_index.db")
    assert not index.has_seen(kind="grammar", topic_key="past-simple", text="She went home")
    index.register(
        kind="grammar",
        topic_key="past-simple",
        text="She went home",
        source_url="https://x.test",
        validation_score=0.9,
    )
    assert index.has_seen(kind="grammar", topic_key="past-simple", text="She went home")
