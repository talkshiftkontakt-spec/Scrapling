from __future__ import annotations

PL_QUERY_TEMPLATES = [
    "{topic} ćwiczenia",
    "{topic} zadania",
    "{topic} ćwiczenia z odpowiedziami",
    "{topic} test gramatyczny",
    "site:ang.pl {topic}",
    "{topic} uzupełnij zdania",
]

PL_KNOWN_SITES = [
    "ang.pl",
    "englishdotcom.pl",
    "testy-egzaminacyjne.pl",
    "jezykiobce.pl",
]


def build_pl_queries(topic: str, limit: int = 5) -> list[str]:
    queries = [template.format(topic=topic) for template in PL_QUERY_TEMPLATES]
    return queries[:limit]
