import logging

from src.parsers.platform_public_parser import has_restricted_access_marker, parse


class FakeClient:
    def __init__(self, content: str):
        self.content = content

    def fetch_text(self, url: str) -> str:
        return self.content


def test_platform_public_parser_skips_login_or_captcha_pages(caplog):
    html = "<html><body>请登录后查看职位详情，请完成验证码安全验证。</body></html>"
    source = {
        "name": "Boss 直聘",
        "type": "platform_public",
        "url": "https://example.com/jobs",
        "selectors": {"item": "article.job", "title": "h2"},
    }

    with caplog.at_level(logging.WARNING):
        jobs = parse(source, FakeClient(html))

    assert jobs == []
    assert has_restricted_access_marker(html) is True
    assert "Restricted platform page skipped" in caplog.text


def test_platform_public_parser_extracts_public_job_items_and_filters_keywords():
    html = """
    <html><body>
      <article class="job">
        <h2>CAE 有限元仿真实习生</h2>
        <span class="company">公开平台样例公司</span>
        <span class="location">上海</span>
        <p class="description">Abaqus Python 结构分析 暑期实习 3个月</p>
        <a href="https://example.com/apply/cae">apply</a>
      </article>
      <article class="job">
        <h2>市场运营实习生</h2>
        <span class="company">公开平台样例公司</span>
        <span class="location">北京</span>
        <p class="description">销售支持和市场活动</p>
        <a href="https://example.com/apply/marketing">apply</a>
      </article>
    </body></html>
    """
    source = {
        "name": "公开招聘平台样例",
        "type": "platform_public",
        "url": "https://example.com/jobs",
        "source_label": "sample_platform_public",
        "must_contain_any_keywords": ["CAE", "有限元", "仿真"],
        "selectors": {
            "item": "article.job",
            "title": "h2",
            "company": ".company",
            "location": ".location",
            "description": ".description",
            "link": "a[href]",
        },
    }

    jobs = parse(source, FakeClient(html))

    assert len(jobs) == 1
    assert jobs[0].title == "CAE 有限元仿真实习生"
    assert jobs[0].company_name == "公开平台样例公司"
    assert jobs[0].source == "sample_platform_public"

