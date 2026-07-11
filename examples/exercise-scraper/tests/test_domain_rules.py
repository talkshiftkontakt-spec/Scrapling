from __future__ import annotations

from exercise_scraper.extract.domain_rules import load_domain_rules, match_domain_rule


def test_domain_rules_load() -> None:
    rules = load_domain_rules()
    assert "agendaweb.org" in rules
    assert "perfect-english-grammar.com" in rules


def test_match_domain_rule_strips_www() -> None:
    rule = match_domain_rule("https://www.agendaweb.org/verbs/past_simple.html")
    assert rule is not None
    assert "li" in " ".join(rule.selectors)
