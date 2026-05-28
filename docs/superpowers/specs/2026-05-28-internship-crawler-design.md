# Internship Crawler Design

## Goal

Build a compliant daily internship collection and screening tool for mechanics, mechanical engineering, CAE, finite element, structural simulation, reliability, robotics force-control, and haptics roles.

## Scope

The MVP collects from configured public sources and manual imports, then cleans, scores, stores, and reports jobs. It does not bypass login, CAPTCHA, platform anti-scraping controls, paywalls, or terms restrictions.

## Architecture

- `src/crawler`: compliant HTTP access with request delay, User-Agent, robots.txt checks, logging, and local sample file support.
- `src/parsers`: source-specific parsers for RSS/Atom, static HTML, and public JSON APIs.
- `src/importer`: manual CSV/TXT/HTML import for platforms that should not be crawled automatically.
- `src/cleaner`: company/location normalization, duplicate removal, and field extraction.
- `src/scorer`: keyword and rule-based scoring with A/B/C/D recommendation levels.
- `src/storage`: dated Excel, CSV, and SQLite output.
- `src/report`: dated Markdown daily report listing A/B jobs.
- `config`: YAML-compatible configuration for sources, keywords, and scoring rules.

## Data Flow

Configured sources or manual import files produce `JobPosting` records. The cleaner normalizes and deduplicates them. The scorer enriches each job with scores, level, skills, recommendation reasons, and risks. Storage writes `日期_实习信息.xlsx/csv/db`, and the reporter writes `日期_实习信息_日报.md`.

## Compliance

The source config records disabled/manual-only platforms such as LinkedIn, Boss 直聘, 实习僧, 牛客, 智联, 猎聘, 前程无忧, and 微信公众号. The crawler checks robots.txt for HTTP(S) sources and logs skipped pages.

## Testing

Tests cover manual CSV import, cleaning and deduplication, scoring/risk behavior, dated output naming, SQLite writes, and Markdown report generation.

