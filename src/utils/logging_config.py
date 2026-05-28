from __future__ import annotations

import logging
from pathlib import Path


def configure_logging(log_dir: str | Path = "logs") -> None:
    target = Path(log_dir)
    target.mkdir(parents=True, exist_ok=True)
    log_file = target / "internship_crawler.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
        force=True,
    )

