"""Deterministic artwork export helpers with post-export checks."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any

from PIL import Image

from engine.svg import build_svg


def export_artwork(layout: dict[str, Any], profile: dict[str, Any],
                   output_dir: str | Path, include_psd: bool = True) -> dict[str, Any]:
    import cairosvg

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    stem = profile["id"]
    svg = build_svg(layout, profile)
    svg_path = out / f"{stem}.svg"
    png_path = out / f"{stem}.png"
    pdf_path = out / f"{stem}.pdf"
    svg_path.write_text(svg, encoding="utf-8")

    cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=str(png_path),
                     output_width=profile["width_px"], output_height=profile["height_px"])
    with Image.open(png_path) as image:
        image.load()
        image.save(png_path, dpi=(profile["dpi"], profile["dpi"]))
        if image.size != (profile["width_px"], profile["height_px"]):
            raise ValueError("PNG pixel dimensions failed validation")

    cairosvg.svg2pdf(bytestring=svg.encode("utf-8"), write_to=str(pdf_path))
    result: dict[str, Any] = {
        "svg": str(svg_path), "png": str(png_path), "pdf": str(pdf_path),
        "validated": {"png_dimensions": [profile["width_px"], profile["height_px"]],
                      "png_dpi": profile["dpi"], "svg_exists": svg_path.is_file(),
                      "pdf_exists": pdf_path.is_file()},
        "warnings": []
    }

    # ImageMagick's PSD writer produces a flattened compatibility PSD. It is
    # explicitly not advertised as a layered/editable source document.
    convert = shutil.which("magick") or shutil.which("convert")
    if include_psd and convert:
        psd_path = out / f"{stem}.psd"
        command = [convert, str(png_path), str(psd_path)]
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
        if completed.returncode == 0 and psd_path.is_file():
            result["psd"] = str(psd_path)
            result["warnings"].append("PSD is flattened; editable layers are not provided.")
        else:
            result["warnings"].append("PSD export failed: " + (completed.stderr[-500:] or "unknown error"))
    elif include_psd:
        result["warnings"].append("PSD not generated: install ImageMagick. No fake PSD file was created.")
    return result
