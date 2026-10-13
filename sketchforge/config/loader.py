"""YAML loader with layered overrides.

Resolution order, lowest to highest priority:

1. ``config/default.yaml`` shipped with the package.
2. ``config/local.yaml`` in the working directory, if present.
3. Environment overrides of the form ``SKETCHFORGE__APP__MAX_DIMENSION``.

The double-underscore separator maps to nested keys.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from sketchforge.config.schema import AppConfig

_PACKAGE_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_PATH = _PACKAGE_ROOT / "config" / "default.yaml"
_ENV_PREFIX = "SKETCHFORGE__"


def _deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _coerce(raw: str) -> Any:
    lowered = raw.strip().lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    try:
        return int(raw)
    except ValueError:
        pass
    try:
        return float(raw)
    except ValueError:
        return raw


def _apply_env_overrides(tree: dict[str, Any]) -> dict[str, Any]:
    for env_key, raw_value in os.environ.items():
        if not env_key.startswith(_ENV_PREFIX):
            continue
        path = [segment.lower() for segment in env_key[len(_ENV_PREFIX):].split("__")]
        cursor = tree
        for segment in path[:-1]:
            cursor = cursor.setdefault(segment, {})
        cursor[path[-1]] = _coerce(raw_value)
    return tree


def load_config(overrides: dict[str, Any] | None = None) -> AppConfig:
    """Load, merge, and validate the runtime configuration.

    Raises:
        FileNotFoundError: if the bundled default config is missing.
        pydantic.ValidationError: if the merged tree does not match the schema.
    """
    if not _DEFAULT_PATH.exists():
        raise FileNotFoundError(f"default config missing at {_DEFAULT_PATH}")

    with _DEFAULT_PATH.open("r", encoding="utf-8") as handle:
        tree: dict[str, Any] = yaml.safe_load(handle) or {}

    local_path = Path.cwd() / "config" / "local.yaml"
    if local_path.exists():
        with local_path.open("r", encoding="utf-8") as handle:
            tree = _deep_merge(tree, yaml.safe_load(handle) or {})

    tree = _apply_env_overrides(tree)
    if overrides:
        tree = _deep_merge(tree, overrides)

    return AppConfig.model_validate(tree)