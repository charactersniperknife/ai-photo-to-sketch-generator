"""Abstract base for sketch styles.

A style owns its own post-processing: hatching, stroke weighting, grain.
The shared pipeline produces an edge map; the style turns that edge map
into something that looks like it came off a real sheet of paper.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np

from sketchforge.config.schema import StyleSpec


class BaseSketchStyle(ABC):
    """Base class every sketch style inherits from."""

    name: str = "base"

    def __init__(self, spec: StyleSpec) -> None:
        self.spec = spec

    @abstractmethod
    def render(self, edge_map: np.ndarray, source: np.ndarray) -> np.ndarray:
        """Turn a float32 edge map into a final uint8 BGR sketch.

        Args:
            edge_map: float32 array in [0, 1], single channel.
            source: the original BGR uint8 image, for tone reference.

        Returns:
            A uint8 BGR image ready to save.
        """

    def _to_bgr(self, gray: np.ndarray) -> np.ndarray:
        import cv2

        eight = (np.clip(gray, 0.0, 1.0) * 255.0).astype(np.uint8)
        return cv2.cvtColor(eight, cv2.COLOR_GRAY2BGR)