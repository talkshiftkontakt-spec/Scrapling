from __future__ import annotations

import argparse
import json
import os
import sys

from ingestion.scrapling.pipeline import DesignIngestionPipeline


def main() -> int:
    parser = argparse.ArgumentParser(description="Design Intelligence ingestion runner")
    subparsers = parser.add_subparsers(dest="command", required=True)

    discover_parser = subparsers.add_parser("discover", help="Discover websites from curated providers")
    discover_parser.add_argument("--limit", type=int, default=50)

    capture_parser = subparsers.add_parser("capture", help="Capture screenshots for pending websites")
    capture_parser.add_argument("--limit", type=int, default=10)

    args = parser.parse_args()
    pipeline = DesignIngestionPipeline(api_base_url=os.environ.get("INGESTION_API_URL", "http://127.0.0.1:3001"))

    if args.command == "discover":
        result = pipeline.discover_all(limit=args.limit)
        print(json.dumps(result, indent=2))
        return 0

    if args.command == "capture":
        result = pipeline.capture_batch(limit=args.limit)
        print(json.dumps(result, indent=2))
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
