import pytest

from engine.profiles import load_profile
from engine.svg import build_svg


def test_svg_uses_profile_canvas_and_escapes_text():
    profile = load_profile("fat_500ml")
    layout = {
        "canvas": {"width_px": 9000, "height_px": 6000, "dpi": 1200},
        "elements": [{"id": "title", "type": "text", "x": 0.5, "y": 0.5,
                      "text": "A & B < C", "font_size": 0.04}],
    }
    svg = build_svg(layout, profile)
    assert 'viewBox="0 0 9000 6000"' in svg
    assert "A &amp; B &lt; C" in svg


def test_svg_rejects_non_monochrome_colors():
    profile = load_profile("fat_500ml")
    layout = {"canvas": {"width_px": 9000, "height_px": 6000, "dpi": 1200},
              "elements": [{"type": "rect", "x": 0, "y": 0, "width": 1,
                            "height": 1, "fill": "#FF0000"}]}
    with pytest.raises(ValueError):
        build_svg(layout, profile)


def test_svg_rejects_wrong_canvas_dimensions():
    profile = load_profile("fat_500ml")
    with pytest.raises(ValueError):
        build_svg({"canvas": {"width_px": 100, "height_px": 100, "dpi": 1200},
                   "elements": []}, profile)
