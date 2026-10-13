"""Heavy charcoal style with film grain."""

from __future__ import annotations

import numpy as np

from sketchforge.styles.base import BaseSketchStyle


class CharcoalStyle(BaseSketchStyle):
    """Charcoal look: crushed blacks, wide tonal range, visible grain."""

    name = "charcoal"

    def render(self, edge_map: np.ndarray, source: np.ndarray) -> np.ndarray:
        grain = float(self.spec.model_extra.get("grain", 0.35))
        gamma = float(self.spec.model_extra.get("contrast_gamma", 1.15))

        toned = np.power(np.clip(edge_map, 0.0, 1.0), gamma)
        rng = np.random.default_rng(seed=0xBEEF)
        noise = rng.normal(0.0, grain * 0.12, toned.shape).astype(np.float32)
        grained = np.clip(toned + noise, 0.0, 1.0)
        return self._to_bgr(grained)