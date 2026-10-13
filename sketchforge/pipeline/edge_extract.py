"""Classical edge-extraction stages.

These are the workhorses: a Laplacian-of-Gaussian pass for soft pencil
contours and an adaptive-threshold pass for hard ink lines. Both register
themselves into the shared stage registry at import time.
"""

from __future__ import annotations

import cv2
import numpy as np

from sketchforge.pipeline.registry import PipelineContext, register_stage


def _dodge_blend(gray: np.ndarray, blur: np.ndarray) -> np.ndarray:
    """Colour-dodge a blurred copy over the source — the classic pencil trick.

    ``result = gray * 255 / (255 - blur)`` with a guard against the divide-by
    blowup where the blurred value approaches white.
    """
    blur = np.clip(blur, 0.0, 254.0)
    return np.clip(gray * 255.0 / (255.0 - blur + 1e-6), 0.0, 255.0)


@register_stage("edge_extract")
def edge_extract(image: np.ndarray, ctx: PipelineContext) -> np.ndarray:
    """Produce a float32 edge map in [0, 1] for the current style.

    Pencil styles get a dodge-blended Laplacian; ink styles get an adaptive
    threshold. Charcoal gets a heavy median blur before the Laplacian so the
    grain reads as texture rather than noise.
    """
    gray = (image * 255.0).astype(np.uint8)
    style = ctx.style

    if style == "ink":
        threshold = float(ctx.config.styles.get("ink", {}).get("threshold", 0.45))
        block = max(3, (gray.shape[0] // 40) | 1)
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,
            blockSize=block, C=int(threshold * 12),
        )
        lines = 255 - binary
        ctx.scratch["ink_binary"] = binary
        return lines.astype(np.float32) / 255.0

    kernel_size = 5 if style == "charcoal" else 3
    if style == "charcoal":
        gray = cv2.medianBlur(gray, kernel_size)

    blurred = cv2.GaussianBlur(gray, (0, 0), sigmaX=1.6)
    if style == "charcoal":
        # LoG with a wider kernel; catches the soft coal smudges.
        laplacian = cv2.Laplacian(blurred, cv2.CV_32F, ksize=5)
    else:
        laplacian = cv2.Laplacian(blurred, cv2.CV_32F, ksize=3)

    edges = np.abs(laplacian)
    edges = edges / (edges.max() + 1e-6)
    dodged = _dodge_blend(gray.astype(np.float32), blurred.astype(np.float32))
    combined = 0.65 * dodged + 0.35 * (edges * 255.0)
    return (combined / 255.0).astype(np.float32)