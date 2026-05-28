from __future__ import annotations

import argparse
import logging
from datetime import date
from pathlib import Path

from src.cleaner.pipeline import clean_jobs
from src.crawler.http_client import CompliantHttpClient
from src.importer.manual_import import load_manual_file
from src.parsers.registry import collect_from_sources
from src.report.daily import generate_daily_report
from src.scorer.engine import ScoreEngine
from src.storage.writer import write_outputs
from src.utils.config import load_config, project_root, resolve_project_path
from src.utils.logging_config import configure_logging

LOGGER = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="Internship crawler for CAE/mechanics-oriented roles.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run configured collection pipeline once.")
    run_parser.add_argument("--config", default="config/sources.yaml", help="Path to sources config.")
    run_parser.add_argument("--output-dir", default="data/output", help="Output directory.")
    run_parser.add_argument("--date", default=date.today().isoformat(), help="Run date, YYYY-MM-DD.")
    run_parser.add_argument("--latest", action="store_true", help="Also write jobs_latest.* convenience copies.")

    import_parser = subparsers.add_parser("import", help="Import one manual file and generate outputs.")
    import_parser.add_argument("--file", required=True, help="CSV/TXT/HTML manual import file.")
    import_parser.add_argument("--output-dir", default="data/output", help="Output directory.")
    import_parser.add_argument("--date", default=date.today().isoformat(), help="Run date, YYYY-MM-DD.")

    args = parser.parse_args()
    configure_logging(project_root() / "logs")

    if args.command == "run":
        run_pipeline(
            config_path=args.config,
            output_dir=args.output_dir,
            run_date=args.date,
            write_latest=args.latest,
        )
    elif args.command == "import":
        run_manual_import(args.file, args.output_dir, args.date)


def run_pipeline(config_path: str, output_dir: str, run_date: str, write_latest: bool = False) -> dict[str, Path]:
    config = load_config(resolve_project_path(config_path))
    global_config = config.get("global", {})
    client = CompliantHttpClient(
        user_agent=global_config.get(
            "user_agent",
            "internship-crawler/0.1 (+https://github.com/TedzzZhang/internship-crawler; compliance contact: personal use)",
        ),
        delay_seconds=float(global_config.get("request_delay_seconds", 2.0)),
        timeout_seconds=int(global_config.get("timeout_seconds", 20)),
    )
    jobs = collect_from_sources(config.get("sources", []), client)
    LOGGER.info("Collected %s raw jobs", len(jobs))
    return process_and_write(jobs, output_dir, run_date, write_latest=write_latest)


def run_manual_import(file_path: str, output_dir: str, run_date: str) -> dict[str, Path]:
    jobs = load_manual_file(resolve_project_path(file_path))
    LOGGER.info("Imported %s manual jobs from %s", len(jobs), file_path)
    return process_and_write(jobs, output_dir, run_date)


def process_and_write(
    jobs,
    output_dir: str,
    run_date: str,
    write_latest: bool = False,
) -> dict[str, Path]:
    cleaned = clean_jobs(jobs)
    scorer = ScoreEngine.default()
    scored = [scorer.score(job) for job in cleaned]
    output_path = resolve_project_path(output_dir)
    paths = write_outputs(scored, output_path, run_date=run_date, write_latest=write_latest)
    report_path = generate_daily_report(scored, output_path, run_date=run_date)
    paths["report"] = report_path
    LOGGER.info("Generated outputs: %s", {key: str(value) for key, value in paths.items()})
    return paths


if __name__ == "__main__":
    main()

