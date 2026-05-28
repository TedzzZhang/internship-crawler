from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_config(path: str | Path) -> dict[str, Any]:
    config_path = Path(path)
    text = config_path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        loaded = yaml.safe_load(text)
        return loaded or {}
    except ModuleNotFoundError:
        return json.loads(text)


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_project_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return project_root() / candidate

