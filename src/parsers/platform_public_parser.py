from __future__ import annotations

import logging
import re
from typing import Any
from urllib.parse import urljoin

from src.crawler.http_client import CompliantHttpClient
from src.models import JobPosting
from src.parsers import static_page_parser

LOGGER = logging.getLogger(__name__)

RESTRICTED_ACCESS_MARKERS = [
    "请登录",
    "登录后查看",
    "登录后",
    "未登录",
    "账号登录",
    "扫码登录",
    "验证码",
    "安全验证",
    "滑块",
    "访问过于频繁",
    "verify you are human",
    "captcha",
    "security check",
    "sign in",
    "login required",
    "authentication required",
    "enable cookies",
]


def parse(source: dict[str, Any], client: CompliantHttpClient) -> list[JobPosting]:
    html = client.fetch_text(source["url"])
    if has_restricted_access_marker(html):
        LOGGER.warning(
            "Restricted platform page skipped: %s. Use manual import or an official authorized API.",
            source.get("name", source.get("url")),
        )
        return []

    try:
        jobs = static_page_parser.parse_with_bs4(html, source)
    except ModuleNotFoundError:
        jobs = static_page_parser.parse_with_regex(html, source)

    jobs = normalize_platform_links(jobs, source["url"])
    keywords = source.get("must_contain_any_keywords", [])
    if keywords:
        jobs = [job for job in jobs if contains_any(job.text_for_matching(), keywords)]
    return jobs


def has_restricted_access_marker(html: str) -> bool:
    compact = re.sub(r"\s+", " ", html).lower()
    return any(marker.lower() in compact for marker in RESTRICTED_ACCESS_MARKERS)


def contains_any(text: str, keywords: list[str]) -> bool:
    lower = text.lower()
    return any(keyword.lower() in lower for keyword in keywords)


def normalize_platform_links(jobs: list[JobPosting], base_url: str) -> list[JobPosting]:
    for job in jobs:
        if job.application_link:
            job.application_link = urljoin(base_url, job.application_link)
    return jobs

