"""Configuration loading and schema validation."""

from sketchforge.config.loader import load_config
from sketchforge.config.schema import AppConfig

__all__ = ["load_config", "AppConfig"]