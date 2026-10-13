"""Disk I/O for photos and rendered sketches.

All reads go through :func:`load_image`, which normalises every input to a
3-channel uint8 BGR array — the format OpenCV expects. Everything downstream
can then assume a single, boring representation.
"""

from __future__ import annotations

import logging
from pathlib import Path

import cv2
import numpy as np

logger = logging.getLogger(__name__)

_SUPPORTED = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}


class ImageLoadError(RuntimeError):
    """Raised when an input file cannot be decoded as an image."""


def load_image(path: str | Path, max_dimension: int = 4096) -> np.ndarray:
    """Read ``path`` as a 3-channel BGR uint8 array.

    Inputs larger than ``max_dimension`` on the long edge are downscaled with
    area interpolation, which is the cheapest way to avoid a 12-second
    Laplacian pass on a 60-megapixel phone photo.

    Returns:
        A contiguous ``(H, W, 3)`` uint8 array in BGR order.

    Raises:
        ImageLoadError: if the file is missing, unreadable, or zero-sized.
    """
    resolved = Path(path)
    if not resolved.exists():
        raise ImageLoadError(f"input not found: {resolved}")
    if resolved.suffix.lower() not in _SUPPORTED:
        raise ImageLoadError(f"unsupported extension: {resolved.suffix}")

    # cv2.imdecode handles non-ASCII Windows paths that cv2.imread chokes on.
    raw = np.fromfile(str(resolved), dtype=np.uint8)
    image = cv2.imdecode(raw, cv2.IMREAD_COLOR)
    if image is None or image.size == 0:
        raise ImageLoadError(f"could not decode image: {resolved}")

    height, width = image.shape[:2]
    long_edge = max(height, width)
    if long_edge > max_dimension:
        scale = max_dimension / long_edge
        new_size = (int(width * scale), int(height * scale))
        image = cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)
        logger.debug("downscaled %s from %dx%d to %dx%d", resolved, width, height, *new_size)

    return np.ascontiguousarray(image)


def save_image(
    image: np.ndarray,
    path: str | Path,
    jpeg_quality: int = 95,
) -> Path:
    """Write ``image`` to ``path``, creating parent directories as needed.

    PNG and TIFF are written losslessly; JPEG and WebP honour ``jpeg_quality``.
    Encoding goes through ``cv2.imencode`` for the same non-ASCII-path reason
    as the loader.
    """
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)

    suffix = target.suffix.lower() or ".png"
    params: list[int] = []
    if suffix in {".jpg", ".jpeg"}:
        params = [cv2.IMWRITE_JPEG_QUALITY, int(jpeg_quality)]
    elif suffix == ".webp":
        params = [cv2.IMWRITE_WEBP_QUALITY, int(jpeg_quality)]

    ok, buffer = cv2.imencode(suffix, image, params)
    if not ok:
        raise ImageLoadError(f"failed to encode {target}")
    buffer.tofile(str(target))
    return target