from __future__ import annotations

import json
from typing import Any

from src.crawler.http_client import CompliantHttpClient
from src.models import JobPosting


def parse(source: dict[str, Any], client: CompliantHttpClient) -> list[JobPosting]:
    content = client.fetch_text(source["url"])
    payload = json.loads(content)
    items = value_at_path(payload, source.get("items_path", ""))
    if isinstance(items, dict):
        items = list(items.values())
    if not isinstance(items, list):
        return []
    field_map = source.get("field_map", {})
    return [job_from_item(item, source, field_map) for item in items if isinstance(item, dict)]


def value_at_path(payload: Any, path: str) -> Any:
    current = payload
    if not path:
        return current
    for part in path.split("."):
        if isinstance(current, dict):
            current = current.get(part, [])
        else:
            return []
    return current


def job_from_item(item: dict[str, Any], source: dict[str, Any], field_map: dict[str, str]) -> JobPosting:
    def mapped(name: str, default: str = "") -> str:
        key = field_map.get(name, name)
        value = value_at_path(item, key)
        return str(value or default)

    return JobPosting(
        company_name=mapped("company_name", source.get("company_name", "")),
        company_type=source.get("company_type", ""),
        title=mapped("title"),
        location=mapped("location"),
        internship_time=mapped("internship_time"),
        salary=mapped("salary"),
        education=mapped("education"),
        major_requirement=mapped("major_requirement"),
        raw_description=mapped("raw_description"),
        application_link=mapped("application_link"),
        source=source.get("source_label", source.get("name", "json_api")),
        publish_date=mapped("publish_date"),
        deadline=mapped("deadline"),
    )

