# Internship Crawler Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a runnable Python MVP that collects, imports, cleans, scores, exports, and reports internship jobs for mechanics/CAE-oriented candidates.

**Architecture:** The project uses focused packages under `src/` for crawler, parsers, manual import, cleaning, scoring, storage, reporting, and utilities. All source definitions and scoring inputs live under `config/`, and generated dated outputs live under `data/output/`.

**Tech Stack:** Python standard library, openpyxl, optional BeautifulSoup/feedparser/PyYAML/Playwright, pytest.

---

### Task 1: Project Skeleton and Tests

**Files:**
- Create: `tests/test_scoring.py`
- Create: `tests/test_cleaner_importer.py`
- Create: `tests/test_outputs.py`
- Create: `requirements.txt`

- [x] Write tests for scoring high-value CAE roles and downgrading sales/marketing roles.
- [x] Write tests for manual CSV import and duplicate cleaning.
- [x] Write tests for dated Excel/CSV/SQLite/report output naming.
- [x] Run `python -m pytest -q` and confirm the tests fail because implementation modules are missing.

### Task 2: Core Data and Scoring

**Files:**
- Create: `src/models.py`
- Create: `src/scorer/engine.py`

- [x] Implement `JobPosting` with all required output fields.
- [x] Implement keyword matching, score components, A/B/C/D levels, recommendation reasons, and risk warnings.
- [x] Run `python -m pytest -q` and fix scoring thresholds until tests pass.

### Task 3: Cleaner, Importer, Storage, Report

**Files:**
- Create: `src/cleaner/pipeline.py`
- Create: `src/importer/manual_import.py`
- Create: `src/storage/writer.py`
- Create: `src/report/daily.py`

- [x] Implement company/location normalization, duplicate removal, and field extraction.
- [x] Implement CSV/TXT/HTML manual import.
- [x] Implement dated Excel, CSV, and SQLite output.
- [x] Implement dated Markdown daily report.
- [x] Run `python -m pytest -q` and confirm all tests pass.

### Task 4: Public Source Parsers and CLI

**Files:**
- Create: `src/crawler/http_client.py`
- Create: `src/parsers/rss_parser.py`
- Create: `src/parsers/static_page_parser.py`
- Create: `src/parsers/json_api_parser.py`
- Create: `src/parsers/registry.py`
- Create: `src/main.py`

- [x] Implement compliant HTTP/local file reader with robots.txt, delay, User-Agent, errors, and logging.
- [x] Implement RSS/Atom, static HTML, and public JSON API parsers.
- [x] Implement CLI commands `run` and `import`.
- [x] Run `python -m src.main run --date 2026-05-28` against sample sources.

### Task 5: Config, Samples, Docs, Daily Scripts

**Files:**
- Create: `config/sources.yaml`
- Create: `config/keywords.yaml`
- Create: `config/scoring_rules.yaml`
- Create: `data/samples/*`
- Create: `run_daily.ps1`
- Create: `run_daily.sh`
- Create: `README.md`

- [x] Add sample public static HTML, RSS, JSON, manual CSV, and WeChat text files.
- [x] Add company and platform source templates with compliance notes.
- [x] Document install, configuration, adding companies, manual import, output review, scheduling, scoring adjustment, and compliance.
- [x] Generate sample dated outputs under `data/output/`.

### Task 6: Verification and Publish

**Files:**
- Modify: all project files as needed.

- [x] Run `python -m pytest -q`.
- [x] Run `python -m src.main run --date 2026-05-28`.
- [x] Inspect generated output names.
- [ ] Initialize git, commit, add remote `https://github.com/TedzzZhang/internship-crawler.git`, and push.
