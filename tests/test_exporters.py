from pathlib import Path

from PIL import Image

from engine.exporters import export_artwork


def test_exports_svg_png_pdf_and_reports_psd_status(tmp_path: Path):
    profile = {
        "id": "test_small", "width_px": 120, "height_px": 80, "dpi": 1200,
        "physical_width_mm": 2.54, "physical_height_mm": 1.6933333333
    }
    layout = {
        "canvas": {"width_px": 120, "height_px": 80, "dpi": 1200},
        "elements": [{"id": "title", "type": "text", "x": 0.5, "y": 0.5,
                      "text": "TEST", "font_size": 0.1}]
    }
    result = export_artwork(layout, profile, tmp_path)
    assert Path(result["svg"]).is_file()
    assert Path(result["png"]).is_file()
    assert Path(result["pdf"]).is_file()
    with Image.open(result["png"]) as image:
        assert image.size == (120, 80)
        assert round(image.info["dpi"][0]) == 1200
    assert "warnings" in result
    if "psd" not in result:
        assert any("PSD not generated" in warning for warning in result["warnings"])
