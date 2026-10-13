"""Pydantic models describing the on-disk configuration.

The YAML in ``config/default.yaml`` is validated against :class:`AppConfig`
on load. Any key not declared here is rejected, which keeps typos in
hand-edited configs from silently doing nothing.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class AppSection(BaseModel):
    name: str = "SketchForge"
    version: str
    output_dir: Path = Path("outputs")
    max_dimension: int = Field(default=4096, ge=256, le=16384)
    preserve_exif: bool = False


class PipelineSection(BaseModel):
    stages: list[str] = Field(min_length=1)
    worker_threads: int = Field(default=4, ge=1, le=32)


class StyleSpec(BaseModel):
    enabled: bool = True
    # Style-specific knobs are free-form; each style module reads what it needs.
    model_config = {"extra": "allow"}

    @field_validator("enabled")
    @classmethod
    def _must_be_bool(cls, value: bool) -> bool:
        return bool(value)


class ModelSection(BaseModel):
    backend: Literal["onnx", "torch", "none"] = "onnx"
    checkpoint: Path | None = None
    device: Literal["cpu", "cuda"] = "cpu"
    input_size: int = Field(default=512, ge=128, le=2048)


class IOSection(BaseModel):
    formats: list[str] = Field(default_factory=lambda: ["png", "jpg"])
    jpeg_quality: int = Field(default=95, ge=1, le=100)
    strip_metadata: bool = True


class AppConfig(BaseModel):
    app: AppSection
    pipeline: PipelineSection
    styles: dict[str, StyleSpec]
    model: ModelSection
    io: IOSection

    model_config = {"extra": "forbid"}