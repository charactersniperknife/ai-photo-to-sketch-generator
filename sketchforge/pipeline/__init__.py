"""Ordered image-processing pipeline.

Stages are resolved by name from :data:`STAGE_REGISTRY` and applied in the
order declared in the config. Each stage is a pure function
``(image, context) -> image``.
"""

from sketchforge.pipeline.registry import STAGE_REGISTRY, PipelineContext, run_pipeline

__all__ = ["STAGE_REGISTRY", "PipelineContext", "run_pipeline"]