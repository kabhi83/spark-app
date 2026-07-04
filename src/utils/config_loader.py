"""YAML/environment-variable configuration loader"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml


def load_config(config_path: str | Path) -> dict[str|Any]:
    """
    Load a YAML config file and overlay environment variable overrides.

    Environment variables are matched by upper-casing dotted keys
    e.g. - ``job.input.path`` can be overridden by ``JOB__INPUT__PATH
    (double underscore as separator)

    Args:
        :param config_path: Path to the YAML config file

    :return:
        Merged configuration dictionary
    """
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with path.open() as f:
        config: dict[str: Any] = yaml.safe_load(f) or {}

    _apply_env_overrides(config)
    return config


def _apply_env_overrides(config: dict, prefix:str = "") -> None:
    """Recursively apply environment variable overrides to config dict"""
    for key, value in config.items():
        env_key = (f"{prefix}__{key}" if prefix else key).upper().replace(".", "__")
        if isinstance(value, dict):
            _apply_env_overrides(value, prefix=env_key)
        else:
            env_val = os.getenv(env_key)
            if env_val is not None:
                config[key] = _cast(env_val, type(value))


def _cast(value: str, target_type: type) -> Any:
    """Cast a string env var to the target type."""
    if target_type == bool:
        return value.lower() in ("true", "1", "yes")
    if target_type == int:
        return int(value)
    if target_type == float:
        return float(value)
    return value
