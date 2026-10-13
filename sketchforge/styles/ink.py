"""High-contrast ink style."""

from __future__ import annotations

import cv2
import numpy as np

from sketchforge.styles.base import BaseSketchStyle


class InkStyle(BaseSketchStyle):
    """Pen-and-ink look: hard lines, no hatching, slight stroke weight."""

    name = "ink"

    def render(self, edge_map: np.ndarray, source: np.ndarray) -> np.ndarray:
        weight = int(round(float(self.spec.model_extra.get("stroke_weight", 1.8))))
        weight = max(1, min(5, weight))

        lines = (edge_map > 0.5).astype(np.float32)
        if weight > 1:
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (weight, weight))
            lines = cv2.dilate(lines, kernel, iterations=1)
        return self._to_bgr(1.0 - lines)