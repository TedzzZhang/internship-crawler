from __future__ import annotations

import copy
import re
from dataclasses import dataclass, field

from src.models import JobPosting


DEFAULT_KEYWORDS: dict[str, list[str]] = {
    "professional": [
        "CAE",
        "仿真",
        "结构仿真",
        "结构分析",
        "有限元",
        "力学",
        "固体力学",
        "材料力学",
        "机械研发",
        "机械设计",
        "结构设计",
        "可靠性",
        "疲劳",
        "振动",
        "NVH",
        "热仿真",
        "热结构耦合",
        "接触力学",
        "超弹性",
        "软材料",
        "机器人",
        "触觉",
        "力控",
        "数字孪生",
        "FEA",
        "FEM",
        "finite element",
        "simulation",
        "structural analysis",
        "mechanical design",
        "mechanical engineering",
        "solid mechanics",
        "computational mechanics",
        "material modeling",
        "hyperelastic",
        "contact mechanics",
        "durability",
        "fatigue",
        "vibration",
        "thermal simulation",
        "reliability",
        "robotics",
        "haptics",
        "force control",
        "digital twin",
    ],
    "software": [
        "Abaqus",
        "ANSYS",
        "HyperMesh",
        "OptiStruct",
        "LS-DYNA",
        "COMSOL",
        "Nastran",
        "Adams",
        "MATLAB",
        "Python",
        "SolidWorks",
        "CATIA",
        "Creo",
        "Simulink",
    ],
    "technical_depth": [
        "建模",
        "模型",
        "实验验证",
        "结构设计",
        "可靠性分析",
        "数据处理",
        "仿真建模",
        "研发项目",
        "有限元分析",
        "test validation",
        "modeling",
        "validation",
        "data processing",
        "R&D",
        "research",
        "simulation model",
    ],
    "growth": [
        "mentor",
        "导师",
        "真实项目",
        "研发项目",
        "转正",
        "跨部门",
        "cross-functional",
        "conversion",
        "ownership",
    ],
    "time": [
        "暑期实习",
        "summer intern",
        "summer internship",
        "2026 summer",
        "3个月",
        "三个月",
        "2个月",
        "两个月",
        "10周",
        "12周",
        "2-3 months",
        "3 months",
    ],
    "resume_match": [
        "Abaqus",
        "MATLAB",
        "力学",
        "固体力学",
        "软材料",
        "接触",
        "实验数据",
        "数据处理",
        "Python",
        "hyperelastic",
        "contact",
        "finite element",
    ],
    "negative": [
        "销售",
        "市场",
        "运营",
        "人事",
        "财务",
        "行政",
        "培训班",
        "广告",
        "sales",
        "marketing",
        "operation",
        "hr",
        "finance",
        "admin",
        "training ad",
    ],
    "full_time_only": [
        "全职",
        "不接受实习",
        "full-time only",
        "full time only",
    ],
}

DEFAULT_COMPANY_VALUES: dict[str, int] = {
    "知名外企": 15,
    "大厂": 15,
    "车企": 14,
    "新能源车/电池": 14,
    "机器人": 14,
    "高端制造": 13,
    "科研院所": 13,
    "高校": 10,
}

PREFERRED_LOCATIONS = ["北京", "天津", "上海", "苏州", "深圳", "广州", "杭州", "南京", "远程"]


@dataclass(slots=True)
class ScoreEngine:
    keywords: dict[str, list[str]] = field(default_factory=lambda: copy.deepcopy(DEFAULT_KEYWORDS))
    company_values: dict[str, int] = field(default_factory=lambda: DEFAULT_COMPANY_VALUES.copy())

    @classmethod
    def default(cls) -> "ScoreEngine":
        return cls()

    def score(self, job: JobPosting) -> JobPosting:
        text = job.text_for_matching()
        professional_hits = match_keywords(text, self.keywords["professional"])
        software_hits = match_keywords(text, self.keywords["software"])
        depth_hits = match_keywords(text, self.keywords["technical_depth"])
        growth_hits = match_keywords(text, self.keywords["growth"])
        time_hits = match_keywords(text, self.keywords["time"])
        resume_hits = match_keywords(text, self.keywords["resume_match"])
        negative_hits = match_keywords(text, self.keywords["negative"])
        full_time_hits = match_keywords(text, self.keywords["full_time_only"])

        relevance = min(30, len(professional_hits) * 5 + len(software_hits) * 2)
        technical_depth = min(20, len(depth_hits) * 4 + len(software_hits) * 2 + min(8, len(professional_hits) * 2))
        company_value = self._company_score(job)
        growth = min(10, len(growth_hits) * 3)
        location = 8 if any(city in job.location for city in PREFERRED_LOCATIONS) else 4 if job.location else 0
        time_score = min(8, len(time_hits) * 4)
        resume = min(9, len(resume_hits) * 2)

        total = relevance + technical_depth + company_value + growth + location + time_score + resume
        risk_parts: list[str] = []
        if negative_hits:
            total -= min(30, 10 + len(negative_hits) * 5)
            risk_parts.append("疑似低相关或排除类岗位：" + "、".join(negative_hits))
        if full_time_hits:
            total -= 25
            risk_parts.append("疑似全职限制：" + "、".join(full_time_hits))
        if not job.raw_description.strip() and not job.jd_summary.strip():
            total -= 15
            risk_parts.append("JD 不明确，建议人工复核")

        job.professional_relevance_score = max(0, relevance)
        job.technical_depth_score = max(0, technical_depth)
        job.total_score = max(0, min(100, total))
        job.skill_keywords = unique_preserve_order(professional_hits + software_hits + job.skill_keywords)
        job.job_direction = job.job_direction or infer_direction(job.skill_keywords, job.title)
        job.jd_summary = job.jd_summary or summarize(job.raw_description)
        job.risk_warning = "；".join(risk_parts) if risk_parts else "暂无明显风险"
        job.recommendation_level = level_from_score(job.total_score)
        if negative_hits or full_time_hits:
            job.recommendation_level = "D"
        job.recommendation_reason = build_reason(job, professional_hits, software_hits, depth_hits, growth_hits)
        return job

    def _company_score(self, job: JobPosting) -> int:
        for company_type, score in self.company_values.items():
            if company_type and company_type in job.company_type:
                return score
        if job.company_name in {
            "Apple",
            "Tesla",
            "Microsoft",
            "Bosch",
            "Siemens",
            "GE",
            "ABB",
            "Schneider Electric",
            "Honeywell",
            "CATL",
            "BYD",
            "NIO",
            "Li Auto",
            "Xpeng",
            "Huawei",
            "DJI",
            "Xiaomi",
            "Lenovo",
        }:
            return 13
        return 8 if job.company_name else 0


def match_keywords(text: str, keywords: list[str]) -> list[str]:
    hits: list[str] = []
    lower = text.lower()
    for keyword in keywords:
        if not keyword:
            continue
        pattern = re.escape(keyword.lower())
        if re.search(pattern, lower):
            hits.append(keyword)
    return unique_preserve_order(hits)


def unique_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        key = value.lower()
        if key not in seen:
            seen.add(key)
            result.append(value)
    return result


def infer_direction(keywords: list[str], title: str) -> str:
    text = " ".join(keywords) + " " + title
    if any(term in text for term in ["机器人", "触觉", "力控", "robotics", "haptics"]):
        return "机器人结构/力控/触觉"
    if any(term in text for term in ["热仿真", "热结构耦合", "thermal"]):
        return "热仿真/热结构耦合"
    if any(term in text for term in ["可靠性", "疲劳", "durability", "fatigue", "reliability"]):
        return "可靠性/疲劳/NVH"
    if any(term in text for term in ["CAE", "有限元", "FEA", "FEM", "仿真"]):
        return "CAE/有限元/结构仿真"
    if any(term in text for term in ["机械", "设计", "mechanical"]):
        return "机械研发/结构设计"
    return "待人工确认"


def summarize(description: str, max_length: int = 120) -> str:
    compact = " ".join(description.split())
    if len(compact) <= max_length:
        return compact
    return compact[: max_length - 3] + "..."


def level_from_score(score: int) -> str:
    if score >= 80:
        return "A"
    if score >= 65:
        return "B"
    if score >= 50:
        return "C"
    return "D"


def build_reason(
    job: JobPosting,
    professional_hits: list[str],
    software_hits: list[str],
    depth_hits: list[str],
    growth_hits: list[str],
) -> str:
    if job.recommendation_level == "D":
        return "不建议优先投递：岗位与力学/机械/仿真研发方向匹配度不足或存在排除风险。"
    reasons: list[str] = []
    if professional_hits:
        reasons.append("专业相关度高，命中 " + "、".join(professional_hits[:6]))
    if software_hits:
        reasons.append("技能匹配，涉及 " + "、".join(software_hits[:5]))
    if depth_hits:
        reasons.append("技术深度较好，包含 " + "、".join(depth_hits[:4]))
    if growth_hits:
        reasons.append("成长性信号明确，出现 " + "、".join(growth_hits[:3]))
    return "；".join(reasons) if reasons else "可作为备选，建议人工确认 JD 细节。"
