from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from src.crawler.http_client import CompliantHttpClient
from src.importer.manual_import import load_manual_file
from src.models import JobPosting
from src.parsers import json_api_parser, platform_public_parser, rss_parser, static_page_parser
from src.utils.config import resolve_project_path

LOGGER = logging.getLogger(__name__)


def collect_from_sources(sources: list[dict[str, Any]], client: CompliantHttpClient) -> list[JobPosting]:
    jobs: list[JobPosting] = []
    for source in sources:
        if not source.get("enabled", False):
            LOGGER.info("Source disabled: %s (%s)", source.get("name"), source.get("compliance_note", ""))
            continue
        try:
            jobs.extend(parse_source(source, client))
        except PermissionError as exc:
            LOGGER.warning("Skipped source by compliance rule: %s", exc)
        except Exception as exc:
            LOGGER.exception("Failed to parse source %s: %s", source.get("name"), exc)
    return jobs


def parse_source(source: dict[str, Any], client: CompliantHttpClient) -> list[JobPosting]:
    source_type = source.get("type")
    if source_type == "rss":
        return rss_parser.parse(source, client)
    if source_type == "static_html":
        return static_page_parser.parse(source, client)
    if source_type == "json_api":
        return json_api_parser.parse(source, client)
    if source_type == "platform_public":
        return platform_public_parser.parse(source, client)
    if source_type in {"manual_csv", "manual_text", "manual_html"}:
        path = Path(source.get("path") or source.get("url") or "")
        return load_manual_file(resolve_project_path(path))
    if source_type in {"manual_only", "disabled_platform"}:
        LOGGER.info("Manual-only source skipped: %s", source.get("name"))
        return []
    LOGGER.warning("Unknown source type %s for %s", source_type, source.get("name"))
    return []
