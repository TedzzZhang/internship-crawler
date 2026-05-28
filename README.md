# 实习招聘信息每日自动采集与筛选工具

面向力学、机械、固体力学、CAE 仿真、结构仿真、有限元分析、机械研发、可靠性、机器人力控/触觉等方向的实习岗位采集与筛选 MVP。

本项目只处理公开网页、企业公开招聘页、公开 RSS/API，以及你手动提供的链接、HTML、CSV 或文本。默认不会绕过登录、验证码、反爬、付费墙或平台访问限制。

## 1. 项目目标

- 每日从配置的公开来源采集实习招聘信息。
- 对岗位做去重、字段提取、关键词识别、风险标注和综合评分。
- 按 A/B/C/D 给出推荐等级。
- 导出 Excel、CSV、SQLite 和 Markdown 日报。
- 对 LinkedIn、Boss 直聘、实习僧、牛客、智联、猎聘、前程无忧、微信公众号等平台，提供“受限公开采集”模板：只访问公开、robots/条款允许、无需登录或验证码的页面；触发限制时自动跳过并改用手动导入。

## 2. 安装方式

建议使用 Python 3.11+。

```bash
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install -r requirements.txt
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

说明：`playwright` 是可选增强依赖，只有公开页面必须渲染、且不涉及登录/验证码时才考虑使用。当前 MVP 默认 parser 不需要启动浏览器。

## 3. 如何运行一次采集

```bash
python -m src.main run
```

指定日期：

```bash
python -m src.main run --date 2026-05-28
```

输出文件会按日期命名：

```text
data/output/2026-05-28_实习信息.xlsx
data/output/2026-05-28_实习信息.csv
data/output/2026-05-28_实习信息.db
data/output/2026-05-28_实习信息_日报.md
```

如需同时生成最新结果快捷副本：

```bash
python -m src.main run --latest
```

## 4. 如何配置招聘来源

编辑 `config/sources.yaml`。虽然扩展名是 `.yaml`，当前文件采用 JSON/YAML 兼容写法，因此没有安装 PyYAML 时也能读取。

一个静态公开招聘页示例：

```json
{
  "name": "Example Careers",
  "type": "static_html",
  "enabled": true,
  "url": "https://example.com/careers/interns",
  "company_name": "Example",
  "company_type": "高端制造",
  "source_label": "example_careers",
  "selectors": {
    "item": "article.job",
    "title": "h2",
    "location": ".location",
    "description": ".description",
    "link": "a[href]"
  }
}
```

支持的来源类型：

- `static_html`：公开静态网页。
- `rss`：公开 RSS/Atom。
- `json_api`：公开 JSON API。
- `platform_public`：招聘平台公开页的受限采集模板，会检测登录、验证码、安全验证等限制标记。
- `manual_csv` / `manual_text` / `manual_html`：手动导入。
- `manual_only`：记录不适合自动采集的平台，运行时跳过。

受限平台示例：

```json
{
  "name": "Boss 直聘",
  "type": "platform_public",
  "enabled": false,
  "url": "https://www.zhipin.com/web/geek/job?query=CAE",
  "source_label": "boss_public_restricted",
  "must_contain_any_keywords": ["CAE", "有限元", "仿真", "结构", "机械"],
  "compliance_note": "受限公开采集模板：不处理 Cookie、登录态、验证码或风控；触发限制则跳过并改用手动导入。"
}
```

## 5. 如何添加新公司

1. 在 `config/sources.yaml` 的 `sources` 数组里新增一项。
2. 确认页面是公开可访问的，不需要登录、验证码或绕过风控。
3. 检查网站 robots.txt 和使用条款。
4. 选择合适 parser：
   - 有 RSS：优先 `rss`。
   - 有公开 JSON：使用 `json_api`。
   - 普通 HTML：使用 `static_html` 并配置 CSS selectors。
5. 先设置 `enabled: false`，人工检查后再改为 `true`。

## 6. 如何查看输出结果

- Excel：打开 `data/output/日期_实习信息.xlsx`。
- CSV：打开 `data/output/日期_实习信息.csv`。
- SQLite：数据库文件为 `data/output/日期_实习信息.db`，表名是 `jobs`。
- 日报：打开 `data/output/日期_实习信息_日报.md`。

## 7. 如何手动导入

CSV：

```bash
python -m src.main import --file data/samples/manual_jobs.csv
```

微信聊天记录或复制文本：

```bash
python -m src.main import --file data/samples/wechat_export_sample.txt
```

HTML：

```bash
python -m src.main import --file path/to/job_page.html
```

CSV 支持常见列名：`company`、`title`、`location`、`description`、`link`、`source`、`salary`、`education`、`major`、`internship_time`。中文列名如 `公司名称`、`岗位名称`、`地点`、`岗位描述`、`投递链接` 也支持。

## 8. 如何调整关键词和评分规则

- 关键词：`config/keywords.yaml`
- 评分说明：`config/scoring_rules.yaml`
- 当前实际评分实现：`src/scorer/engine.py`

默认权重：

```text
专业相关度 30
技术深度   20
企业价值   15
成长性     10
地点匹配度 8
时间匹配度 8
简历匹配度 9
```

等级：

```text
A: >= 80，强烈推荐投递
B: 65-79，值得投递
C: 50-64，可备选
D: < 50，不建议优先投递
```

## 9. 每日自动运行

### Windows 任务计划程序

在 PowerShell 中测试：

```powershell
.\run_daily.ps1
```

任务计划程序设置建议：

- 操作：启动程序
- 程序：`powershell.exe`
- 参数：`-ExecutionPolicy Bypass -File "C:\path\to\internship-crawler\run_daily.ps1"`
- 触发器：每天一次，例如上午 09:00

### macOS/Linux cron

先给脚本执行权限：

```bash
chmod +x run_daily.sh
```

编辑 crontab：

```bash
crontab -e
```

每天 09:00 运行：

```cron
0 9 * * * /path/to/internship-crawler/run_daily.sh
```

## 10. 合规注意事项

- 不绕过登录、验证码、反爬、付费墙或平台访问限制。
- 默认请求间隔为 2 秒，可在 `config/sources.yaml` 的 `global.request_delay_seconds` 调整。
- HTTP 客户端会使用自定义 User-Agent，并检查 robots.txt。
- 如果 robots.txt 不允许抓取，程序会跳过并写日志。
- LinkedIn、Boss 直聘、实习僧、牛客、智联、猎聘、前程无忧、微信公众号已配置为 `platform_public` 受限采集模板，但默认 `enabled: false`；确认公开可访问、robots/条款允许后可启用，触发登录、验证码、安全验证、App 跳转或访问限制时会跳过并写日志。
- 不要把本工具用于高频、大规模、商业化抓取。

## 11. 项目结构

```text
.
├── README.md
├── requirements.txt
├── run_daily.ps1
├── run_daily.sh
├── config/
├── data/
│   ├── raw/
│   ├── processed/
│   ├── output/
│   └── samples/
├── logs/
├── src/
│   ├── main.py
│   ├── crawler/
│   ├── parsers/
│   ├── importer/
│   ├── cleaner/
│   ├── scorer/
│   ├── storage/
│   ├── report/
│   └── utils/
└── tests/
```

## 12. 运行测试

```bash
python -m pytest -q
```

当前 sample 数据只用于验证流程，不代表真实招聘信息。
