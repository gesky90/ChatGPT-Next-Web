from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class ConfigError(ValueError):
    pass


def load_yaml(path: str | Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ConfigError(f"Invalid yaml at {path}: root should be a mapping")
    return data


def validate_project_config(cfg: dict[str, Any]) -> None:
    required = ["project", "data", "analysis", "output"]
    for key in required:
        if key not in cfg:
            raise ConfigError(f"project config missing key: {key}")

    outcome_type = cfg["analysis"]["outcome"]["type"]
    if outcome_type not in {"continuous", "binary", "survival"}:
        raise ConfigError("analysis.outcome.type must be one of continuous|binary|survival")

    if outcome_type == "survival":
        for key in ["time_column", "event_column"]:
            value = cfg["analysis"]["outcome"].get(key)
            if not value or str(value).startswith("REPLACE_ME"):
                raise ConfigError(f"survival outcome needs valid {key}")


def validate_placeholder(cfg: dict[str, Any], path: str = "") -> list[str]:
    placeholders: list[str] = []
    if isinstance(cfg, dict):
        for k, v in cfg.items():
            child_path = f"{path}.{k}" if path else str(k)
            placeholders.extend(validate_placeholder(v, child_path))
    elif isinstance(cfg, list):
        for i, v in enumerate(cfg):
            child_path = f"{path}[{i}]"
            placeholders.extend(validate_placeholder(v, child_path))
    else:
        if isinstance(cfg, str) and "REPLACE_ME" in cfg:
            placeholders.append(path)
    return placeholders
