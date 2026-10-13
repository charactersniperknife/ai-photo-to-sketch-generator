"""Stage registry and pipeline runner."""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass, field

import numpy as np

from sketchforge.config.schema import AppConfig

logger = logging.getLogger(__name__)

Stage = Callable[[np.ndarray, "PipelineContext"], np.ndarray]


@dataclass
class PipelineContext:
    """Mutable state threaded through every stage."""

    config: AppConfig
    style: str
    scratch: dict[str, np.ndarray] = field(default_factory=dict)


def _register(name: str) -> Callable[[Stage], Stage]:
    def decorator(func: Stage) -> Stage:
        STAGE_REGISTRY[name] = func
        return func

    return decorator


STAGE_REGISTRY: dict[str, Stage] = {}


def register_stage(name: str, func: Stage) -> None:
    """Public registration hook for third-party stages."""
    STAGE_REGISTRY[name] = func


def run_pipeline(
    image: np.ndarray,
    config: AppConfig,
    style: str,
) -> np.ndarray:
    """Apply every configured stage in order and return the result.

    Raises:
        KeyError: if a stage name in the config has no registered callable.
    """
    context = PipelineContext(config=config, style=style)
    current = image
    for stage_name in config.pipeline.stages:
        try:
            stage = STAGE_REGISTRY[stage_name]
        except KeyError as exc:
            raise KeyError(
                f"unknown pipeline stage '{stage_name}'; "
                f"registered: {sorted(STAGE_REGISTRY)}"
            ) from exc
        logger.debug("running stage %s for style %s", stage_name, style)
        current = stage(current, context)
    return current