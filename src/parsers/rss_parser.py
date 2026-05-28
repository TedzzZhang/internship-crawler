from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Any

from src.crawler.http_client import CompliantHttpClient
from src.models import JobPosting


def parse(source: dict[str, Any], client: CompliantHttpClient) -> list[JobPosting]:
    content = client.fetch_text(source["url"])
    try:
        import feedparser  # type: ignore

        feed = feedparser.parse(content)
        return [
            JobPosting(
                company_name=source.get("company_name", ""),
                company_type=source.get("company_type", ""),
                title=entry.get("title", ""),
                raw_description=entry.get("summary", "") or entry.get("description", ""),
                application_link=entry.get("link", ""),
                source=source.get("source_label", source.get("name", "rss")),
                publish_date=entry.get("published", ""),
            )
            for entry in feed.entries
        ]
    except ModuleNotFoundError:
        return parse_with_element_tree(content, source)


def parse_with_element_tree(content: str, source: dict[str, Any]) -> list[JobPosting]:
    root = ET.fromstring(content)
    jobs: list[JobPosting] = []
    for item in root.findall(".//item"):
        jobs.append(
            JobPosting(
                company_name=source.get("company_name", ""),
                company_type=source.get("company_type", ""),
                title=text_of(item, "title"),
                raw_description=text_of(item, "description"),
                application_link=text_of(item, "link"),
                source=source.get("source_label", source.get("name", "rss")),
                publish_date=text_of(item, "pubDate"),
            )
        )
    if jobs:
        return jobs
    namespace = {"atom": "http://www.w3.org/2005/Atom"}
    for entry in root.findall(".//atom:entry", namespace):
        link = entry.find("atom:link", namespace)
        jobs.append(
            JobPosting(
                company_name=source.get("company_name", ""),
                company_type=source.get("company_type", ""),
                title=text_of(entry, "atom:title", namespace),
                raw_description=text_of(entry, "atom:summary", namespace) or text_of(entry, "atom:content", namespace),
                application_link=link.attrib.get("href", "") if link is not None else "",
                source=source.get("source_label", source.get("name", "rss")),
                publish_date=text_of(entry, "atom:updated", namespace),
            )
        )
    return jobs


def text_of(element: ET.Element, tag: str, namespace: dict[str, str] | None = None) -> str:
    child = element.find(tag, namespace or {})
    return "".join(child.itertext()).strip() if child is not None else ""

