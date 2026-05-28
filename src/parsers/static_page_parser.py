from __future__ import annotations

import re
from typing import Any

from src.crawler.http_client import CompliantHttpClient
from src.models import JobPosting


def parse(source: dict[str, Any], client: CompliantHttpClient) -> list[JobPosting]:
    html = client.fetch_text(source["url"])
    try:
        from bs4 import BeautifulSoup  # type: ignore

        return parse_with_bs4(html, source)
    except ModuleNotFoundError:
        return parse_with_regex(html, source)


def parse_with_bs4(html: str, source: dict[str, Any]) -> list[JobPosting]:
    from bs4 import BeautifulSoup  # type: ignore

    soup = BeautifulSoup(html, "html.parser")
    selectors = source.get("selectors", {})
    item_selector = selectors.get("item", ".job, article, li")
    jobs: list[JobPosting] = []
    for item in soup.select(item_selector):
        title_node = item.select_one(selectors.get("title", "h1,h2,h3,a"))
        if title_node is None:
            continue
        link_node = item.select_one(selectors.get("link", "a[href]"))
        link = link_node.get("href", "") if link_node is not None else ""
        description_node = item.select_one(selectors.get("description", ".description,.jd,p"))
        location_node = item.select_one(selectors.get("location", ".location"))
        company_node = item.select_one(selectors.get("company", ".company"))
        jobs.append(
            JobPosting(
                company_name=text_or_default(company_node, source.get("company_name", "")),
                company_type=source.get("company_type", ""),
                title=title_node.get_text(" ", strip=True),
                location=text_or_default(location_node, source.get("location", "")),
                raw_description=text_or_default(description_node, item.get_text(" ", strip=True)),
                application_link=link,
                source=source.get("source_label", source.get("name", "static_html")),
            )
        )
    return jobs


def parse_with_regex(html: str, source: dict[str, Any]) -> list[JobPosting]:
    blocks = re.findall(r"<article[^>]*class=[\"'][^\"']*job[^\"']*[\"'][^>]*>(.*?)</article>", html, flags=re.I | re.S)
    if not blocks:
        blocks = re.findall(r"<li[^>]*class=[\"'][^\"']*job[^\"']*[\"'][^>]*>(.*?)</li>", html, flags=re.I | re.S)
    jobs: list[JobPosting] = []
    for block in blocks:
        title = clean_html(first_match(block, [r"<h[1-3][^>]*>(.*?)</h[1-3]>", r"<a[^>]*>(.*?)</a>"]))
        if not title:
            continue
        link = first_match(block, [r"<a[^>]*href=[\"']([^\"']+)[\"']"])
        location = clean_html(first_match(block, [r"class=[\"']location[\"'][^>]*>(.*?)<"]))
        company = clean_html(first_match(block, [r"class=[\"']company[\"'][^>]*>(.*?)<"]))
        description = clean_html(first_match(block, [r"class=[\"'](?:description|jd)[\"'][^>]*>(.*?)</"]))
        jobs.append(
            JobPosting(
                company_name=company or source.get("company_name", ""),
                company_type=source.get("company_type", ""),
                title=title,
                location=location,
                raw_description=description or clean_html(block),
                application_link=link,
                source=source.get("source_label", source.get("name", "static_html")),
            )
        )
    return jobs


def text_or_default(node: Any, default: str) -> str:
    return node.get_text(" ", strip=True) if node is not None else default


def first_match(text: str, patterns: list[str]) -> str:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.I | re.S)
        if match:
            return match.group(1).strip()
    return ""


def clean_html(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", value).strip()
