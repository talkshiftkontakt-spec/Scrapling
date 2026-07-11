from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml

from exercise_scraper.extract.selectors import EXERCISE_SELECTORS

from exercise_scraper.config_paths import CONFIG_DIR


@dataclass(frozen=True)
class DomainRule:
    hostname: str
    selectors: list[str]
    min_confidence: float | None = None


def load_domain_rules(path: Path | None = None) -> dict[str, DomainRule]:
    config_path = path or (CONFIG_DIR / "domain_rules.yaml")
    raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    rules: dict[str, DomainRule] = {}
    for hostname, payload in (raw.get("domains") or {}).items():
        rules[hostname.lower()] = DomainRule(
            hostname=hostname.lower(),
            selectors=list(payload.get("selectors", EXERCISE_SELECTORS)),
            min_confidence=payload.get("min_confidence"),
        )
    return rules


def hostname_from_url(url: str) -> str:
    host = urlparse(url).netloc.lower()
    return host[4:] if host.startswith("www.") else host


def match_domain_rule(url: str, rules: dict[str, DomainRule] | None = None) -> DomainRule | None:
    rules = rules or load_domain_rules()
    host = hostname_from_url(url)
    if host in rules:
        return rules[host]
    for key, rule in rules.items():
        if host.endswith("." + key):
            return rule
    return None
