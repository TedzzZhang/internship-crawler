from __future__ import annotations

import re

from src.models import JobPosting
from src.scorer.engine import DEFAULT_KEYWORDS, match_keywords, unique_preserve_order


COMPANY_ALIASES = {
    "bosch china": "Bosch",
    "博世": "Bosch",
    "siemens china": "Siemens",
    "西门子": "Siemens",
    "宁德时代": "CATL",
    "catl": "CATL",
    "比亚迪": "BYD",
    "大疆": "DJI",
    "华为": "Huawei",
    "小米": "Xiaomi",
    "联想": "Lenovo",
    "蔚来": "NIO",
    "理想": "Li Auto",
    "小鹏": "Xpeng",
}

LOCATION_ALIASES = {
    "shanghai": "上海",
    "上海市": "上海",
    "beijing": "北京",
    "北京市": "北京",
    "shenzhen": "深圳",
    "深圳市": "深圳",
    "suzhou": "苏州",
    "苏州市": "苏州",
    "hangzhou": "杭州",
    "杭州 市": "杭州",
    "nanjing": "南京",
    "guangzhou": "广州",
    "tianjin": "天津",
}


def clean_jobs(jobs: list[JobPosting]) -> list[JobPosting]:
    cleaned: list[JobPosting] = []
    seen: set[tuple[str, str, str]] = set()
    for job in jobs:
        normalize_job(job)
        key = job.dedupe_key()
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(job)
    return cleaned


def normalize_job(job: JobPosting) -> JobPosting:
    job.company_name = normalize_company(job.company_name)
    job.location = normalize_location(job.location)
    job.salary = job.salary or extract_salary(job.raw_description)
    job.education = job.education or extract_education(job.raw_description)
    job.major_requirement = job.major_requirement or extract_major(job.raw_description)
    job.internship_time = job.internship_time or extract_internship_time(job.raw_description)
    keywords = match_keywords(job.text_for_matching(), DEFAULT_KEYWORDS["professional"] + DEFAULT_KEYWORDS["software"])
    job.skill_keywords = unique_preserve_order(job.skill_keywords + keywords)
    return job


def normalize_company(company: str) -> str:
    value = company.strip()
    key = value.lower()
    return COMPANY_ALIASES.get(key, COMPANY_ALIASES.get(value, value))


def normalize_location(location: str) -> str:
    value = location.strip()
    if not value:
        return ""
    parts = re.split(r"[/,，|;；\s]+", value)
    for part in parts:
        if not part:
            continue
        key = part.lower()
        if key in LOCATION_ALIASES:
            return LOCATION_ALIASES[key]
        if part in LOCATION_ALIASES:
            return LOCATION_ALIASES[part]
    return LOCATION_ALIASES.get(value.lower(), value.replace("市", ""))


def extract_salary(text: str) -> str:
    patterns = [
        r"\d+\s*-\s*\d+\s*(?:元/天|/天|k/月|K/月|元/月)",
        r"\d+\s*(?:元/天|/天|k/月|K/月|元/月)",
    ]
    return first_match(text, patterns)


def extract_education(text: str) -> str:
    return first_match(text, [r"(本科及以上|硕士及以上|博士|硕士|本科|研究生)"])


def extract_major(text: str) -> str:
    return first_match(text, [r"(力学|机械|车辆工程|材料|航空航天|机器人|自动化|计算力学|固体力学)[^，。,.;；\n]{0,20}"])


def extract_internship_time(text: str) -> str:
    return first_match(
        text,
        [
            r"(?:暑期实习|summer intern(?:ship)?|2026 summer)[^，。,.;；\n]{0,30}",
            r"(?:每周\s*\d+\s*天|实习\s*\d+\s*个月|[23]\s*个月|2-3 months|3 months)",
        ],
    )


def first_match(text: str, patterns: list[str]) -> str:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(0).strip()
    return ""

