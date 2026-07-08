#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from exercise_scraper.validation.quality import validate_file


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate scraped exercises and keep top 3.")
    parser.add_argument("input", type=Path, help="Path to exercises.json")
    parser.add_argument("--output", type=Path, default=None, help="Optional output report path")
    parser.add_argument("--limit", type=int, default=3, help="How many top exercises to keep")
    args = parser.parse_args()

    report = validate_file(args.input, args.output, limit=args.limit)
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
