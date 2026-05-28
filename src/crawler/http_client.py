from __future__ import annotations

import logging
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from pathlib import Path

from src.utils.config import resolve_project_path

LOGGER = logging.getLogger(__name__)


class CompliantHttpClient:
    def __init__(self, user_agent: str, delay_seconds: float = 2.0, timeout_seconds: int = 20):
        self.user_agent = user_agent
        self.delay_seconds = delay_seconds
        self.timeout_seconds = timeout_seconds
        self._last_request_at = 0.0
        self._robots_cache: dict[str, urllib.robotparser.RobotFileParser] = {}

    def fetch_text(self, url_or_path: str) -> str:
        if is_local_path(url_or_path):
            path = local_path(url_or_path)
            LOGGER.info("Reading local source: %s", path)
            return path.read_text(encoding="utf-8")

        if not self.can_fetch(url_or_path):
            LOGGER.warning("Skipped by robots.txt: %s", url_or_path)
            raise PermissionError(f"robots.txt disallows fetching {url_or_path}")

        self._respect_delay()
        request = urllib.request.Request(url_or_path, headers={"User-Agent": self.user_agent})
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                charset = response.headers.get_content_charset() or "utf-8"
                return response.read().decode(charset, errors="replace")
        except urllib.error.HTTPError as exc:
            LOGGER.warning("HTTP error %s for %s", exc.code, url_or_path)
            raise
        except urllib.error.URLError as exc:
            LOGGER.warning("URL error for %s: %s", url_or_path, exc)
            raise

    def can_fetch(self, url: str) -> bool:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            return True
        base = f"{parsed.scheme}://{parsed.netloc}"
        parser = self._robots_cache.get(base)
        if parser is None:
            parser = urllib.robotparser.RobotFileParser()
            parser.set_url(urllib.parse.urljoin(base, "/robots.txt"))
            try:
                parser.read()
            except Exception as exc:  # robots.txt failures are logged and treated as unknown.
                LOGGER.info("Could not read robots.txt for %s: %s", base, exc)
            self._robots_cache[base] = parser
        return parser.can_fetch(self.user_agent, url)

    def _respect_delay(self) -> None:
        elapsed = time.monotonic() - self._last_request_at
        if elapsed < self.delay_seconds:
            time.sleep(self.delay_seconds - elapsed)
        self._last_request_at = time.monotonic()


def is_local_path(value: str) -> bool:
    parsed = urllib.parse.urlparse(value)
    return parsed.scheme in {"", "file"}


def local_path(value: str) -> Path:
    parsed = urllib.parse.urlparse(value)
    if parsed.scheme == "file":
        return Path(urllib.request.url2pathname(parsed.path))
    return resolve_project_path(value)

