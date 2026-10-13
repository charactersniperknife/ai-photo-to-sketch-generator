"""Concrete pipeline stages: normalise, denoise, tone map.

Edge extraction and line refinement live in their own modules because they
carry the interesting math.
"""

from __future__ import annotations

import cv2
import numpy as np

from sketchforge.pipeline.registry import PipelineContext, register_stage


@register_stage("normalise")
def normalise(image: np.ndarray, _ctx: PipelineContext) -> np.ndarray:
    """Convert to grayscale-friendly float and stretch contrast gently.

    Output is float32 in [0, 1]. Everything after this stage can assume that
    range, which removes a whole class of "why is my output 255× too bright"
    bugs.
    """
    if image.ndim == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    normalised = gray.astype(np.float32) / 255.0
    # CLAHE on the 0-1 range; clip limit tuned to keep halos off skin tones.
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    stretched = clahe.apply((normalised * 255).astype(np.uint8))
    return stretched.astype(np.float32) / 255.0


@register_stage("denoise")
def denoise(image: np.ndarray, ctx: PipelineContext) -> np.ndarray:
    """Edge-preserving smoothing before edge extraction.

    Bilateral filtering keeps real contours sharp while flattening the sensor
    noise that would otherwise turn into speckle in the sketch.
    """
    radius = int(ctx.config.styles.get(ctx.style, {}).get("soften_radius", 1) * 3)
    radius = max(1, radius)
    return cv2.bilateralFilter(image, d=radius, sigmaColor=0.08, sigmaSpace=radius)


@register_stage("tone_map")
def tone_map(image: np.ndarray, ctx: PipelineContext) -> np.ndarray:
    """Final contrast / gamma pass, then back to uint8 BGR for saving."""
    spec = ctx.config.styles.get(ctx.style, {})
    gamma = float(spec.get("contrast_gamma", 1.0))
    corrected = np.power(np.clip(image, 0.0, 1.0), 1.0 / max(gamma, 0.01))
    eight_bit = (corrected * 255.0).clip(0, 255).astype(np.uint8)
    return cv2.cvtColor(eight_bit, cv2.COLOR_GRAY2BGR)