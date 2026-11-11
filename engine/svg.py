"""Deterministic SVG composition and lightweight preview rendering."""
from __future__ import annotations

import html
from pathlib import Path
from typing import Any


def _number(value: Any, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be numeric") from exc
    if not 0 <= number <= 1:
        raise ValueError(f"{label} must be normalized to 0..1")
    return number


def build_svg(layout: dict[str, Any], profile: dict[str, Any]) -> str:
    canvas = layout.get("canvas", {})
    width, height = profile["width_px"], profile["height_px"]
    if canvas.get("width_px") != width or canvas.get("height_px") != height:
        raise ValueError("Layout canvas does not match selected bottle profile")
    if canvas.get("dpi") != profile["dpi"]:
        raise ValueError("Layout DPI does not match selected bottle profile")
    physical_w = profile["physical_width_mm"]
    physical_h = profile["physical_height_mm"]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{physical_w}mm" height="{physical_h}mm" '
        f'viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#FFFFFF"/>',
    ]
    for item in layout.get("elements", []):
        kind = item.get("type")
        x = _number(item.get("x", 0), "x") * width
        y = _number(item.get("y", 0), "y") * height
        fill = item.get("fill", "#000000")
        stroke = item.get("stroke", "none")
        sw = max(0, float(item.get("stroke_width", 0.002))) * min(width, height)
        if fill not in ("#000000", "#FFFFFF", "none") or stroke not in ("#000000", "#FFFFFF", "none"):
            raise ValueError("Only pure black, pure white, or none are permitted")
        if kind == "rect":
            w = _number(item.get("width", 0), "width") * width
            h = _number(item.get("height", 0), "height") * height
            parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
        elif kind == "circle":
            radius = _number(item.get("radius", 0), "radius") * min(width, height)
            parts.append(f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
        elif kind == "line":
            x2 = _number(item.get("x2", 0), "x2") * width
            y2 = _number(item.get("y2", 0), "y2") * height
            parts.append(f'<line x1="{x}" y1="{y}" x2="{x2}" y2="{y2}" stroke="{stroke if stroke != "none" else "#000000"}" stroke-width="{max(sw, 1)}"/>')
        elif kind == "text":
            anchor = item.get("anchor", "middle")
            if anchor not in ("start", "middle", "end"):
                raise ValueError("Text anchor must be start, middle, or end")
            font_size = _number(item.get("font_size", 0.03), "font_size") * min(width, height)
            content = html.escape(str(item.get("text", "")))
            parts.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="DejaVu Sans, sans-serif" font-size="{font_size}" fill="{fill}">{content}</text>')
        else:
            raise ValueError(f"Unsupported SVG element type: {kind}")
    parts.append("</svg>")
    return "\n".join(parts)


def write_svg(layout: dict[str, Any], profile: dict[str, Any], path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(build_svg(layout, profile), encoding="utf-8")
    return target


def render_preview(layout: dict[str, Any], profile: dict[str, Any], path: str | Path,
                   max_width: int = 1600) -> Path:
    import cairosvg

    svg = build_svg(layout, profile)
    output_width = min(max_width, profile["width_px"])
    output_height = max(1, round(output_width * profile["height_px"] / profile["width_px"]))
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=str(target),
                     output_width=output_width, output_height=output_height)
    return target
