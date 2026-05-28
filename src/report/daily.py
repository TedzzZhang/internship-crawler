from __future__ import annotations

from pathlib import Path

from src.models import JobPosting


def generate_daily_report(jobs: list[JobPosting], output_dir: str | Path, run_date: str) -> Path:
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / f"{run_date}_实习信息_日报.md"
    sorted_jobs = sorted(jobs, key=lambda job: job.total_score, reverse=True)
    recommended = [job for job in sorted_jobs if job.recommendation_level in {"A", "B"}]
    lines = [
        f"# {run_date} 实习信息日报",
        "",
        f"- 岗位总数：{len(jobs)}",
        f"- A/B 级岗位：{len(recommended)}",
        "",
        "## 今日优先关注",
        "",
    ]
    if not recommended:
        lines.append("今天没有新增 A/B 级岗位。")
    else:
        lines.extend(
            [
                "| 推荐等级 | 综合评分 | 公司 | 岗位 | 地点 | 推荐理由 | 投递链接 |",
                "| --- | ---: | --- | --- | --- | --- | --- |",
            ]
        )
        for job in recommended:
            lines.append(
                "| "
                + " | ".join(
                    [
                        job.recommendation_level,
                        str(job.total_score),
                        safe_cell(job.company_name),
                        safe_cell(job.title),
                        safe_cell(job.location),
                        safe_cell(job.recommendation_reason),
                        safe_cell(job.application_link),
                    ]
                )
                + " |"
            )
    lines.extend(["", "## 合规提示", "", "本报告仅基于公开页面、公开 RSS/API 或手动导入数据生成；不包含绕过登录、验证码、付费墙或平台限制的采集结果。"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def safe_cell(value: str) -> str:
    return (value or "").replace("|", "/").replace("\n", " ")

