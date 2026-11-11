"""Screening must produce strictly 1-bit output that tracks source tone."""
from __future__ import annotations

import pytest
from PIL import Image

from engine import halftone


def _gradient(w: int = 240, h: int = 120) -> Image.Image:
    img = Image.new("L", (w, h))
    px = img.load()
    for x in range(w):
        v = int(255 * x / max(w - 1, 1))
        for y in range(h):
            px[x, y] = v
    return img


def _flat(value: int, w: int = 160, h: int = 160) -> Image.Image:
    return Image.new("L", (w, h), value)


@pytest.mark.parametrize("method", ["dot_screen", "floyd_steinberg", "ordered_bayer"])
def test_output_is_pure_black_and_white(method):
    out = halftone.screen(_gradient(), method=method, pitch=8)
    assert out.mode == "1"
    assert halftone.is_pure_bw(out), f"{method} produced intermediate tones"


@pytest.mark.parametrize("method", ["dot_screen", "floyd_steinberg", "ordered_bayer"])
def test_dimensions_are_preserved(method):
    src = _gradient(200, 90)
    out = halftone.screen(src, method=method, pitch=8)
    assert out.size == src.size


@pytest.mark.parametrize("method", ["dot_screen", "floyd_steinberg", "ordered_bayer"])
def test_darker_source_yields_more_ink(method):
    light = halftone.screen(_flat(210), method=method, pitch=8)
    dark = halftone.screen(_flat(60), method=method, pitch=8)
    assert halftone.ink_coverage(dark) > halftone.ink_coverage(light)


def test_white_source_prints_nothing():
    out = halftone.screen(_flat(255), method="dot_screen", pitch=8)
    assert halftone.ink_coverage(out) == pytest.approx(0.0, abs=1e-3)


def test_invert_flips_coverage():
    normal = halftone.screen(_flat(60), method="dot_screen", pitch=8)
    flipped = halftone.screen(_flat(60), method="dot_screen", pitch=8, invert=True)
    assert halftone.ink_coverage(flipped) < halftone.ink_coverage(normal)


def test_coverage_is_monotonic_across_tones():
    coverages = [
        halftone.ink_coverage(halftone.screen(_flat(v), method="dot_screen", pitch=8))
        for v in (230, 180, 120, 60, 10)
    ]
    assert coverages == sorted(coverages), coverages


def test_rejects_bad_parameters():
    with pytest.raises(ValueError):
        halftone.dot_screen(_flat(128), pitch=1)
    with pytest.raises(ValueError):
        halftone.ordered_bayer(_flat(128), scale=0)
    with pytest.raises(ValueError):
        halftone.screen(_flat(128), method="nope")
    with pytest.raises(ValueError):
        halftone.dot_screen(_flat(128), contrast=0)
