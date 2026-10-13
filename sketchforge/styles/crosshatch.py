"""Experimental crosshatch style (disabled by default)."""

from __future__ import annotations

import cv2
import numpy as np

from sketchforge.styles.base import BaseSketchStyle


class CrosshatchStyle(BaseSketchStyle):
    """Two-direction hatching meant to read as a pen texture study."""

    name = "crosshatch"

    def render(self, edge_map: np.ndarray, source: np.ndarray) -> np.ndarray:
        height, width = edge_map.shape
        canvas = np.ones((height, width), dtype=np.float32)
        spacing = 6
        for step in range(-height, width, spacing):
            cv2.line(canvas, (step, 0), (step + height, height), 0.0, 1)
        for step in range(-height, width, spacing):
            cv2.line(canvas, (step, height), (step + height, 0), 0.0, 1)
        combined = np.minimum(canvas, edge_map)
        return self._to_bgr(combined)