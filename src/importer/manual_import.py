from __future__ import annotations

import csv
import re
from pathlib import Path

from src.models import JobPosting


COLUMN_MAP = {
    "company": "company_name",
    "公司": "company_name",
    "公司名称": "company_name",
    "title": "title",
    "岗位": "title",
    "岗位名称": "title",
    "location": "location",
    "地点": "location",
    "城市": "location",
    "description": "raw_description",
    "jd": "raw_description",
    "岗位描述": "raw_description",
    "link": "application_link",
    "url": "application_link",
    "投递链接": "application_link",
    "source": "source",
    "来源": "source",
    "salary": "salary",
    "薪资": "salary",
    "education": "education",
    "学历": "education",
    "major": "major_requirement",
    "专业": "major_requirement",
    "internship_time": "internship_time",
    "实习时间": "internship_time",
}


def load_manual_file(path: str | Path) -> list[JobPosting]:
    file_path = Path(path)
    suffix = file_path.suffix.lower()
    if suffix == ".csv":
        return load_manual_csv(file_path)
    if suffix in {".txt", ".md"}:
        return load_manual_text(file_path)
    if suffix in {".html", ".htm"}:
        return load_manual_html(file_path)
    raise ValueError(f"Unsupported manual import file: {file_path}")


def load_manual_csv(path: Path) -> list[JobPosting]:
    jobs: list[JobPosting] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            jobs.append(job_from_row(row, default_source=f"manual:{path.name}"))
    return jobs


def load_manual_text(path: Path) -> list[JobPosting]:
    content = path.read_text(encoding="utf-8")
    blocks = [block.strip() for block in re.split(r"\n\s*\n", content) if block.strip()]
    jobs: list[JobPosting] = []
    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        link = first_url(block)
        title = lines[0] if lines else "手动导入岗位"
        company = infer_company_from_text(block)
        jobs.append(
            JobPosting(
                company_name=company,
                title=title,
                raw_description=block,
                application_link=link,
                source=f"manual:{path.name}",
            )
        )
    return jobs


def load_manual_html(path: Path) -> list[JobPosting]:
    content = path.read_text(encoding="utf-8")
    text = re.sub(r"<[^>]+>", " ", content)
    text = re.sub(r"\s+", " ", text).strip()
    return [
        JobPosting(
            title="手动导入 HTML 岗位",
            raw_description=text,
            application_link=first_url(content),
            source=f"manual:{path.name}",
        )
    ]


def job_from_row(row: dict[str, str], default_source: str) -> JobPosting:
    data: dict[str, str] = {}
    for key, value in row.items():
        mapped = COLUMN_MAP.get(key.strip())
        if mapped:
            data[mapped] = (value or "").strip()
    if not data.get("source"):
        data["source"] = default_source
    return JobPosting(**data)


def first_url(text: str) -> str:
    match = re.search(r"https?://\S+", text)
    return match.group(0).rstrip(").,，。") if match else ""


def infer_company_from_text(text: str) -> str:
    for marker in ["公司：", "公司:", "Company:", "company:"]:
        if marker in text:
            return text.split(marker, 1)[1].splitlines()[0].strip()
    return ""

