"""Soft pencil style with configurable hatching."""

from __future__ import annotations

import cv2
import numpy as np

from sketchforge.styles.base import BaseSketchStyle


class PencilStyle(BaseSketchStyle):
    """Graphite pencil look: soft edges plus directional hatching in shadows."""

    name = "pencil"

    def render(self, edge_map: np.ndarray, source: np.ndarray) -> np.ndarray:
        strength = float(self.spec.model_extra.get("line_strength", 0.72))
        density = int(self.spec.model_extra.get("hatch_density", 3))

        inverted = 1.0 - edge_map
        hatched = self._apply_hatching(inverted, density)
        blended = np.clip(strength * edge_map + (1.0 - strength) * hatched, 0.0, 1.0)
        # Slight warm tint so it reads as paper rather than pure white.
        tinted = self._paper_tint(self._to_bgr(1.0 - blended))
        return tinted

    def _apply_hatching(self, shadow: np.ndarray, density: int) -> np.ndarray:
        """Overlay diagonal line patterns whose opacity scales with darkness."""
        height, width = shadow.shape
        hatch = np.ones_like(shadow)
        for index in range(density):
            offset = int((index + 1) * 4)
            canvas = np.ones_like(shadow)
            for x in range(-height, width, max(4, 12 // density)):
                cv2.line(canvas, (x, 0), (x + height, height), 0.0, 1)
            hatch = np.minimum(hatch, 1.0 - (1.0 - canvas) * (shadow ** 1.5))
            del offset
        return hatch

    @staticmethod
    def _paper_tint(bgr: np.ndarray) -> np.ndarray:
        tint = np.array([235, 240, 245], dtype=np.float32)
        blended = bgr.astype(np.float32) * 0.85 + tint * 0.15
        return blended.clip(0, 255).astype(np.uint8)