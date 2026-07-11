from __future__ import annotations

EN_QUERY_TEMPLATES = [
    "{topic} exercises",
    "{topic} grammar exercises",
    "{topic} worksheet with answers",
    "{topic} fill in the blanks",
    "site:perfect-english-grammar.com {topic}",
    "site:english-grammar.at {topic}",
]

EN_KNOWN_SITES = [
    "perfect-english-grammar.com",
    "english-grammar.at",
    "englishteststore.net",
    "learnenglish.de",
]


def build_en_queries(topic: str, limit: int = 5) -> list[str]:
    queries = [template.format(topic=topic) for template in EN_QUERY_TEMPLATES]
    return queries[:limit]
