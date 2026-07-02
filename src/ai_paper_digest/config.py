from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_CONFIG_PATH = Path("configs/queries.json")


def load_config(path: str | Path = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def ensure_project_dirs() -> None:
    Path("data").mkdir(exist_ok=True)
    Path("reports").mkdir(exist_ok=True)
