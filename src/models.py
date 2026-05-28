from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any


FIELD_LABELS: list[tuple[str, str]] = [
    ("collection_date", "采集日期"),
    ("company_name", "公司名称"),
    ("company_type", "公司类型"),
    ("title", "岗位名称"),
    ("job_direction", "岗位方向"),
    ("recommendation_level", "推荐等级"),
    ("total_score", "综合评分"),
    ("professional_relevance_score", "专业相关度评分"),
    ("technical_depth_score", "技术深度评分"),
    ("location", "地点"),
    ("internship_time", "实习时间"),
    ("salary", "薪资 / 日薪 / 月薪"),
    ("education", "学历要求"),
    ("major_requirement", "专业要求"),
    ("skill_keywords", "技能关键词"),
    ("jd_summary", "JD 摘要"),
    ("recommendation_reason", "推荐理由"),
    ("risk_warning", "风险提示"),
    ("application_link", "投递链接"),
    ("source", "信息来源"),
    ("publish_date", "发布时间"),
    ("deadline", "截止时间"),
    ("is_applied", "是否已投递"),
    ("is_favorite", "是否已收藏"),
    ("notes", "备注"),
]


@dataclass(slots=True)
class JobPosting:
    collection_date: str = field(default_factory=lambda: date.today().isoformat())
    company_name: str = ""
    company_type: str = ""
    title: str = ""
    job_direction: str = ""
    recommendation_level: str = "D"
    total_score: int = 0
    professional_relevance_score: int = 0
    technical_depth_score: int = 0
    location: str = ""
    internship_time: str = ""
    salary: str = ""
    education: str = ""
    major_requirement: str = ""
    skill_keywords: list[str] = field(default_factory=list)
    jd_summary: str = ""
    recommendation_reason: str = ""
    risk_warning: str = ""
    application_link: str = ""
    source: str = ""
    publish_date: str = ""
    deadline: str = ""
    is_applied: bool = False
    is_favorite: bool = False
    notes: str = ""
    raw_description: str = ""

    def text_for_matching(self) -> str:
        parts = [
            self.company_name,
            self.company_type,
            self.title,
            self.job_direction,
            self.location,
            self.internship_time,
            self.education,
            self.major_requirement,
            self.raw_description,
            self.jd_summary,
        ]
        return " ".join(part for part in parts if part)

    def to_output_row(self) -> dict[str, Any]:
        row: dict[str, Any] = {}
        for attr, label in FIELD_LABELS:
            value = getattr(self, attr)
            if isinstance(value, list):
                value = ", ".join(value)
            elif isinstance(value, bool):
                value = "是" if value else "否"
            row[label] = value
        return row

    def dedupe_key(self) -> tuple[str, str, str]:
        return (
            normalize_key(self.company_name),
            normalize_key(self.title),
            normalize_key(self.application_link or self.raw_description[:80]),
        )


def normalize_key(value: str) -> str:
    return "".join(value.lower().split())

