from pathlib import Path

from src.cleaner.pipeline import clean_jobs
from src.importer.manual_import import load_manual_file
from src.models import JobPosting


def test_clean_jobs_removes_duplicates_and_extracts_keywords():
    first = JobPosting(
        company_name="Bosch China",
        title="结构仿真实习生",
        location="Shanghai / 上海",
        raw_description="使用 Abaqus 做有限元、结构仿真和疲劳分析。",
        application_link="https://example.com/1",
        source="sample",
    )
    duplicate = JobPosting(
        company_name="博世",
        title="结构仿真实习生",
        location="上海市",
        raw_description="使用 Abaqus 做有限元、结构仿真和疲劳分析。",
        application_link="https://example.com/1",
        source="sample",
    )

    cleaned = clean_jobs([first, duplicate])

    assert len(cleaned) == 1
    assert cleaned[0].company_name == "Bosch"
    assert cleaned[0].location == "上海"
    assert "Abaqus" in cleaned[0].skill_keywords
    assert "有限元" in cleaned[0].skill_keywords


def test_load_manual_csv_maps_columns_to_job_postings(tmp_path: Path):
    csv_path = tmp_path / "manual_jobs.csv"
    csv_path.write_text(
        "company,title,location,description,link,source\n"
        "DJI,机器人力控实习生,深圳,机器人 力控 触觉 Python MATLAB,https://example.com/dji,manual\n",
        encoding="utf-8",
    )

    jobs = load_manual_file(csv_path)

    assert len(jobs) == 1
    assert jobs[0].company_name == "DJI"
    assert jobs[0].title == "机器人力控实习生"
    assert jobs[0].application_link == "https://example.com/dji"

