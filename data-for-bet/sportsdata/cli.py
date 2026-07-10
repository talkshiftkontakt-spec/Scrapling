from __future__ import annotations

import argparse
import json
from pathlib import Path

from sportsdata.config import DEFAULT_DB_PATH, PipelineConfig
from sportsdata.models import Sport
from sportsdata.pipeline import SportsDataPipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sports data scraping pipeline")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH, help="SQLite database path")
    parser.add_argument(
        "--days-ahead",
        type=int,
        default=None,
        help="Include football fixtures up to N days ahead (default: 45)",
    )
    parser.add_argument(
        "--tennis-days-ahead",
        type=int,
        default=None,
        help="Include tennis fixtures up to N days ahead (default: 14)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("run-all", help="Run full pipeline")
    subparsers.add_parser("fixtures", help="Sync upcoming fixtures")
    subparsers.add_parser("stats", help="Enrich prematch stats")
    subparsers.add_parser("odds", help="Snapshot odds")
    subparsers.add_parser("boost", help="Pre-match boost for games in next 2 hours")
    subparsers.add_parser("backfill", help="Import football-data.co.uk history")
    subparsers.add_parser("results", help="Sync recent finished matches with stats")
    subparsers.add_parser("history", help="Import full historical results (Understat + CSV)")
    stats_backfill_parser = subparsers.add_parser(
        "stats-backfill",
        help="Backfill Flashscore per-match statistics for results missing stats",
    )
    stats_backfill_parser.add_argument(
        "--sport",
        choices=[sport.value for sport in Sport],
        default=Sport.TENNIS.value,
    )
    stats_backfill_parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Max matches to backfill (default: all missing)",
    )
    subparsers.add_parser("health", help="Show pipeline health")

    export_parser = subparsers.add_parser("export", help="Export upcoming events to JSON")
    export_parser.add_argument("--output", type=Path, default=Path("data/upcoming.json"))
    export_parser.add_argument("--sport", choices=[sport.value for sport in Sport], default=None)

    serve_parser = subparsers.add_parser("serve", help="Start API and dashboard")
    serve_parser.add_argument("--host", default="0.0.0.0")
    serve_parser.add_argument("--port", type=int, default=8080)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    config_kwargs: dict[str, object] = {"db_path": args.db}
    if args.days_ahead is not None:
        config_kwargs["days_ahead"] = args.days_ahead
    if args.tennis_days_ahead is not None:
        config_kwargs["tennis_days_ahead"] = args.tennis_days_ahead
    config = PipelineConfig(**config_kwargs)
    pipeline = SportsDataPipeline(config)

    if args.command == "run-all":
        results = pipeline.run_all()
        print(json.dumps([result.to_dict() for result in results], indent=2))
        return

    if args.command == "fixtures":
        print(json.dumps(pipeline.run_fixtures_sync().to_dict(), indent=2))
        return

    if args.command == "stats":
        print(json.dumps(pipeline.run_stats_enrich().to_dict(), indent=2))
        return

    if args.command == "odds":
        print(json.dumps(pipeline.run_odds_snapshot().to_dict(), indent=2))
        return

    if args.command == "boost":
        print(json.dumps(pipeline.run_pre_match_boost().to_dict(), indent=2))
        return

    if args.command == "backfill":
        print(json.dumps(pipeline.run_backfill().to_dict(), indent=2))
        return

    if args.command == "results":
        print(json.dumps(pipeline.run_results_sync().to_dict(), indent=2))
        return

    if args.command == "history":
        print(json.dumps(pipeline.run_history_import().to_dict(), indent=2))
        return

    if args.command == "stats-backfill":
        sport = Sport(args.sport)
        config = PipelineConfig(
            **{
                **config_kwargs,
                **({"stats_backfill_batch_size": args.limit} if args.limit is not None else {}),
            }
        )
        pipeline = SportsDataPipeline(config)
        print(json.dumps(pipeline.run_stats_backfill(sport=sport).to_dict(), indent=2))
        return

    if args.command == "health":
        print(json.dumps(pipeline.health(), indent=2))
        return

    if args.command == "export":
        sport = Sport(args.sport) if args.sport else None
        count = pipeline.export_upcoming_json(args.output, sport=sport)
        print(f"Exported {count} events to {args.output}")
        return

    if args.command == "serve":
        import uvicorn

        uvicorn.run(
            "sportsdata.api.server:create_app",
            factory=True,
            host=args.host,
            port=args.port,
        )
        return


if __name__ == "__main__":
    main()
