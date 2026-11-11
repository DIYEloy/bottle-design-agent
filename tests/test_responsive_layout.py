"""The design must compose correctly on every profile, not just the one it
was authored against."""
from __future__ import annotations

import re

import pytest

from designs import baby_shower
from designs.canvas import _PROFILES, Canvas

PROFILE_IDS = sorted(p.stem for p in _PROFILES.glob("*.json"))


def test_every_profile_is_covered():
    assert set(PROFILE_IDS) == {
        "fat_250ml", "fat_500ml", "fat_1l", "long_500ml", "long_1l"}


@pytest.mark.parametrize("pid", PROFILE_IDS)
def test_builds_without_error(pid):
    svg, c = baby_shower.build(pid)
    assert svg.startswith("<?xml")
    assert svg.rstrip().endswith("</svg>")
    assert f'width="{c.w}"' in svg
    assert f'height="{c.h}"' in svg


@pytest.mark.parametrize("pid", PROFILE_IDS)
def test_nothing_is_placed_outside_the_printable_sector(pid):
    _, c = baby_shower.build(pid)
    assert not c.overflows_printable(), (
        f"{pid}: content crosses the seam overlap "
        f"(printable x {c.x0:.0f}..{c.x1:.0f})")


@pytest.mark.parametrize("pid", PROFILE_IDS)
def test_vertical_extent_stays_on_the_label(pid):
    svg, c = baby_shower.build(pid)
    ys = [float(m) for m in re.findall(r'(?:\sy|y1|y2|cy)="(-?[\d.]+)"', svg)]
    assert ys, "no y coordinates emitted"
    # allow a little slack for stroke width and glyph overhang
    assert min(ys) > -c.h * 0.02, f"{pid}: content above the top edge"
    assert max(ys) < c.h * 1.02, f"{pid}: content below the bottom edge"


@pytest.mark.parametrize("pid,band", [
    ("fat_250ml", "short"),
    ("long_500ml", "medium"),
    ("fat_1l", "medium"),
    ("long_1l", "medium"),
    ("fat_500ml", "tall"),
])
def test_band_selection(pid, band):
    assert Canvas(pid).band == band


@pytest.mark.parametrize("pid", PROFILE_IDS)
def test_printable_sector_matches_the_profile(pid):
    c = Canvas(pid)
    assert int(round(c.pw)) == c.profile["printable_width_px"]
    assert c.x0 > 0, "seam overlap should inset the printable sector"


@pytest.mark.parametrize("pid,expected", [
    ("fat_250ml", "about 1"),
    ("fat_500ml", "about 2"),
    ("long_500ml", "about 2"),
    ("fat_1l", "about 4"),
])
def test_servings_are_derived_from_capacity(pid, expected):
    svg, _ = baby_shower.build(pid)
    assert f"Servings per container: {expected}" in svg


@pytest.mark.parametrize("pid", PROFILE_IDS)
def test_volume_label_matches_capacity(pid):
    svg, c = baby_shower.build(pid)
    ml = c.capacity_ml
    assert (f"/ {ml} mL" in svg) or (f"/ {ml/1000:g} L" in svg)


@pytest.mark.parametrize("pid", PROFILE_IDS)
def test_output_declares_no_colour_other_than_black_and_white(pid):
    svg, _ = baby_shower.build(pid)
    fills = set(re.findall(r'(?:fill|stroke)="(#[0-9A-Fa-f]{6})"', svg))
    assert fills <= {"#000000", "#FFFFFF"}, f"{pid}: stray colour {fills}"


@pytest.mark.parametrize("pid", PROFILE_IDS)
def test_stroke_weights_scale_with_the_canvas(pid):
    c = Canvas(pid)
    assert c.HEAVY > c.MED > c.LIGHT >= c.HAIR > 0


def test_short_canvas_scales_artwork_down():
    short = Canvas("fat_250ml")
    tall = Canvas("fat_500ml")
    assert short.scale < tall.scale, "a short label must shrink its artwork"


def test_text_fitting_shrinks_overlong_strings():
    c = Canvas("fat_250ml")
    big = c.fit_size("Nutrition Facts", 400, 300, "900")
    assert big < 300
    assert c.est_width("Nutrition Facts", big, "900") <= 401


def test_text_fitting_leaves_short_strings_alone():
    c = Canvas("fat_500ml")
    assert c.fit_size("0g", 5000, 60) == 60


def test_unknown_profile_is_rejected():
    with pytest.raises(KeyError):
        Canvas("not_a_profile")


# -- authoritative check: rasterise and measure actual ink bounds ----------
@pytest.mark.parametrize("pid", PROFILE_IDS)
def test_rendered_ink_stays_inside_the_printable_sector(pid):
    cairosvg = pytest.importorskip("cairosvg")
    PIL = pytest.importorskip("PIL")
    from PIL import Image
    import io

    svg, c = baby_shower.build(pid)
    width = 900
    scale = width / c.w
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=width,
                           output_height=max(1, int(c.h * scale)))
    img = Image.open(io.BytesIO(png)).convert("L")
    ink = img.point(lambda v: 255 if v < 200 else 0)
    bbox = ink.getbbox()
    assert bbox is not None, f"{pid}: rendered nothing"

    left_mm = bbox[0] / scale / c.dpi * 25.4
    right_mm = (c.w - bbox[2] / scale) / c.dpi * 25.4
    overlap = c.profile["seam_overlap_mm"]
    tol = 1.0  # mm, for stroke width and glyph overhang at this raster size
    assert left_mm >= overlap - tol, (
        f"{pid}: ink starts {left_mm:.1f}mm from the edge, "
        f"inside the {overlap}mm seam overlap")
    assert right_mm >= overlap - tol, (
        f"{pid}: ink ends {right_mm:.1f}mm from the edge, "
        f"inside the {overlap}mm seam overlap")
