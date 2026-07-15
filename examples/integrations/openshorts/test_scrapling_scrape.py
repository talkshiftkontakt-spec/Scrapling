#!/usr/bin/env python3
"""Quick CLI to test SaaSShorts Scrapling scraper on any URL."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scrapling_scraper import scrape_website


def main() -> None:
    parser = argparse.ArgumentParser(description="Test OpenShorts Scrapling scrape pipeline")
    parser.add_argument("url", help="Product URL, e.g. https://www.lingology.pl")
    parser.add_argument("--json", action="store_true", help="Print full JSON")
    args = parser.parse_args()

    try:
        data = scrape_website(args.url)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    print(f"\nMode      : {data.get('scrape_mode')}")
    print(f"Title     : {data.get('title')}")
    print(f"Pages     : {data.get('pages_scraped')}")
    print(f"Headings  : {len(data.get('headings', []))}")
    print(f"Content   : {len(data.get('main_content', ''))} chars")
    print(f"Meta      : {(data.get('meta_description') or '')[:120]}")
    if data.get("headings"):
        print("\nFirst headings:")
        for h in data["headings"][:5]:
            print(f"  - {h}")


if __name__ == "__main__":
    main()
