"""Convert photographs to strictly black-and-white screened artwork.

This reproduces the technique measured in the supplied THE BAR-ZAAR FAT 250 ml
production file: a photograph carried as a dot screen so the output contains
only black marks and unprinted substrate, never grey ink.

Three methods are available:

``dot_screen``
    Classic halftone. Each cell of a rotated grid gets one dot whose radius
    tracks local tone. Closest to the supplied reference, and the most robust
    on press because the marks are large and regular.

``floyd_steinberg``
    Error-diffusion dithering. Finest detail, but produces isolated single
    pixels that small sublimation dots may not hold.

``ordered_bayer``
    Threshold-matrix dithering. Deterministic and cheap; visible crosshatch
    texture.

All methods return a mode ``"1"`` image. Nothing here calls a model.
"""
from __future__ import annotations

import math
from typing import Literal

from PIL import Image, ImageDraw, ImageOps

Image.MAX_IMAGE_PIXELS = None

Method = Literal["dot_screen", "floyd_steinberg", "ordered_bayer"]

_BAYER8 = (
    (0, 32, 8, 40, 2, 34, 10, 42),
    (48, 16, 56, 24, 50, 18, 58, 26),
    (12, 44, 4, 36, 14, 46, 6, 38),
    (60, 28, 52, 20, 62, 30, 54, 22),
    (3, 35, 11, 43, 1, 33, 9, 41),
    (51, 19, 59, 27, 49, 17, 57, 25),
    (15, 47, 7, 39, 13, 45, 5, 37),
    (63, 31, 55, 23, 61, 29, 53, 21),
)


def _prepare(image: Image.Image, contrast: float, invert: bool) -> Image.Image:
    grey = image.convert("L")
    if contrast != 1.0:
        if contrast <= 0:
            raise ValueError("contrast must be positive")
        mid = 128.0
        grey = grey.point(
            lambda v: max(0, min(255, int(mid + (v - mid) * contrast)))
        )
    if invert:
        grey = ImageOps.invert(grey)
    return grey


def dot_screen(
    image: Image.Image,
    *,
    pitch: int = 12,
    angle: float = 45.0,
    contrast: float = 1.0,
    invert: bool = False,
) -> Image.Image:
    """Classic rotated halftone dot screen.

    ``pitch`` is the cell size in pixels at the image's own resolution. At
    1200 DPI a pitch of 12 gives a 100 line-per-inch screen.
    """
    if pitch < 2:
        raise ValueError("pitch must be at least 2 px")
    grey = _prepare(image, contrast, invert)
    w, h = grey.size

    # Supersample so dot edges stay smooth before the final 1-bit threshold.
    ss = 4
    canvas = Image.new("L", (w * ss, h * ss), 255)
    draw = ImageDraw.Draw(canvas)

    theta = math.radians(angle)
    cos_t, sin_t = math.cos(theta), math.sin(theta)
    # Walk a grid in rotated space wide enough to cover the image corners.
    reach = int(math.hypot(w, h) / pitch) + 2
    max_r = pitch * 0.5 * math.sqrt(2.0)

    for gy in range(-reach, reach + 1):
        for gx in range(-reach, reach + 1):
            # cell centre in rotated space -> image space
            rx, ry = gx * pitch, gy * pitch
            cx = rx * cos_t - ry * sin_t + w / 2.0
            cy = rx * sin_t + ry * cos_t + h / 2.0
            if not (-pitch <= cx <= w + pitch and -pitch <= cy <= h + pitch):
                continue
            sx, sy = int(cx), int(cy)
            if 0 <= sx < w and 0 <= sy < h:
                tone = grey.getpixel((sx, sy))
            else:
                tone = 255
            coverage = (255 - tone) / 255.0
            if coverage <= 0.0:
                continue
            r = max_r * math.sqrt(coverage)
            if r < 0.15:
                continue
            draw.ellipse(
                [(cx - r) * ss, (cy - r) * ss, (cx + r) * ss, (cy + r) * ss],
                fill=0,
            )

    return canvas.resize((w, h), Image.LANCZOS).convert("1")


def floyd_steinberg(
    image: Image.Image, *, contrast: float = 1.0, invert: bool = False
) -> Image.Image:
    """Error-diffusion dither via Pillow's built-in implementation."""
    return _prepare(image, contrast, invert).convert("1", dither=Image.FLOYDSTEINBERG)


def ordered_bayer(
    image: Image.Image,
    *,
    scale: int = 1,
    contrast: float = 1.0,
    invert: bool = False,
) -> Image.Image:
    """8x8 ordered threshold dither. ``scale`` enlarges the matrix cell."""
    if scale < 1:
        raise ValueError("scale must be >= 1")
    grey = _prepare(image, contrast, invert)
    w, h = grey.size
    src = grey.load()
    out = Image.new("1", (w, h), 1)
    dst = out.load()
    for y in range(h):
        row = _BAYER8[(y // scale) % 8]
        for x in range(w):
            threshold = (row[(x // scale) % 8] + 0.5) * 4.0
            dst[x, y] = 0 if src[x, y] < threshold else 1
    return out


def screen(
    image: Image.Image,
    *,
    method: Method = "dot_screen",
    pitch: int = 12,
    angle: float = 45.0,
    contrast: float = 1.0,
    invert: bool = False,
) -> Image.Image:
    """Dispatch to a screening method by name."""
    if method == "dot_screen":
        return dot_screen(image, pitch=pitch, angle=angle,
                          contrast=contrast, invert=invert)
    if method == "floyd_steinberg":
        return floyd_steinberg(image, contrast=contrast, invert=invert)
    if method == "ordered_bayer":
        return ordered_bayer(image, contrast=contrast, invert=invert)
    raise ValueError(f"unknown method: {method!r}")


def ink_coverage(image: Image.Image) -> float:
    """Fraction of the image that is black. Use to sanity-check press load."""
    bw = image.convert("1")
    hist = bw.convert("L").histogram()
    total = sum(hist)
    return hist[0] / total if total else 0.0


def is_pure_bw(image: Image.Image, tolerance: float = 0.0) -> bool:
    """True when the image contains no tones other than pure black and white."""
    hist = image.convert("L").histogram()
    total = sum(hist)
    if not total:
        return True
    mid = total - hist[0] - hist[255]
    return (mid / total) <= tolerance
