from src.models import JobPosting
from src.scorer.engine import ScoreEngine


def test_scores_cae_fea_internship_as_strong_recommendation():
    job = JobPosting(
        company_name="Bosch",
        company_type="知名外企",
        title="CAE Simulation Intern",
        location="上海",
        internship_time="2026 summer intern, 3 months",
        raw_description=(
            "Work on finite element simulation, structural analysis, durability, "
            "Abaqus and Python data processing with mentor support on real R&D projects."
        ),
        application_link="https://example.com/jobs/cae",
        source="sample",
    )

    scored = ScoreEngine.default().score(job)

    assert scored.total_score >= 80
    assert scored.recommendation_level == "A"
    assert "CAE" in scored.skill_keywords
    assert "Abaqus" in scored.skill_keywords
    assert "专业相关" in scored.recommendation_reason


def test_sales_or_marketing_internship_is_downgraded():
    job = JobPosting(
        company_name="Example Auto",
        company_type="车企",
        title="市场销售实习生",
        location="北京",
        raw_description="负责销售支持、市场运营、客户沟通，岗位 JD 不涉及研发或仿真。",
        application_link="https://example.com/jobs/sales",
        source="sample",
    )

    scored = ScoreEngine.default().score(job)

    assert scored.recommendation_level == "D"
    assert scored.total_score < 50
    assert "销售" in scored.risk_warning

