"""Sketch-style implementations and their registry."""

from sketchforge.styles.base import BaseSketchStyle
from sketchforge.styles.charcoal import CharcoalStyle
from sketchforge.styles.crosshatch import CrosshatchStyle
from sketchforge.styles.ink import InkStyle
from sketchforge.styles.pencil import PencilStyle

STYLE_REGISTRY: dict[str, type[BaseSketchStyle]] = {
    "pencil": PencilStyle,
    "ink": InkStyle,
    "charcoal": CharcoalStyle,
    "crosshatch": CrosshatchStyle,
}

__all__ = ["BaseSketchStyle", "STYLE_REGISTRY"]