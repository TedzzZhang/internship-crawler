import sqlite3
from pathlib import Path

from src.models import JobPosting
from src.report.daily import generate_daily_report
from src.scorer.engine import ScoreEngine
from src.storage.writer import write_outputs


def test_write_outputs_uses_date_internship_info_names(tmp_path: Path):
    job = ScoreEngine.default().score(
        JobPosting(
            company_name="Siemens",
            company_type="知名外企",
            title="有限元仿真实习生",
            location="北京",
            raw_description="CAE FEA Abaqus Python 结构分析 暑期实习 3个月 mentor",
            application_link="https://example.com/siemens",
            source="sample",
        )
    )

    paths = write_outputs([job], tmp_path, run_date="2026-05-28")

    assert paths["xlsx"].name == "2026-05-28_实习信息.xlsx"
    assert paths["csv"].name == "2026-05-28_实习信息.csv"
    assert paths["db"].name == "2026-05-28_实习信息.db"
    assert paths["xlsx"].exists()
    assert paths["csv"].exists()
    assert paths["db"].exists()

    with sqlite3.connect(paths["db"]) as connection:
        count = connection.execute("select count(*) from jobs").fetchone()[0]
    assert count == 1


def test_daily_report_lists_ab_jobs(tmp_path: Path):
    job = ScoreEngine.default().score(
        JobPosting(
            company_name="CATL",
            company_type="新能源车/电池",
            title="结构仿真暑期实习生",
            location="上海",
            raw_description="有限元 CAE 热结构耦合 Python Abaqus 真实研发项目 可实习3个月",
            application_link="https://example.com/catl",
            source="sample",
        )
    )

    report_path = generate_daily_report([job], tmp_path, run_date="2026-05-28")

    content = report_path.read_text(encoding="utf-8")
    assert report_path.name == "2026-05-28_实习信息_日报.md"
    assert "CATL" in content
    assert "结构仿真暑期实习生" in content
    assert "| A |" in content

