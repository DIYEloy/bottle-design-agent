"""Profile-aware drawing canvas with a normalised coordinate system.

Designs are authored against the **printable sector** — the area inside the
seam overlap — in normalised coordinates where ``(0, 0)`` is its top-left and
``(1, 1)`` its bottom-right. The canvas converts those to pixels for whatever
profile it was constructed with, so one composition serves every bottle.

Two sizing systems, deliberately:

*Decorative* sizes (``c.s(...)``) scale with the canvas, so artwork keeps its
proportions as the label grows. The scale is ``min(printable_w / 7800,
height / 6000)`` against the FAT 500 ml reference, taking the *smaller* of the
two so a short wide label shrinks its artwork instead of overflowing.

*Furniture* sizes (``c.mm(...)``) are absolute millimetres, because a
nutrition panel must stay legible at a fixed physical size no matter which
bottle it is printed on. Legibility does not scale.

Mixing the two is the point, not an inconsistency.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parent.parent
_PROFILES = _ROOT / "profiles"

#: Reference canvas the stroke weights in style.json were measured against.
REF_W, REF_H = 7800, 6000

BLACK = "#000000"


def load_style() -> dict[str, Any]:
    return json.loads((Path(__file__).resolve().parent / "style.json")
                      .read_text(encoding="utf-8"))


def load_profile(profile_id: str) -> dict[str, Any]:
    path = _PROFILES / f"{profile_id}.json"
    if not path.exists():
        known = sorted(p.stem for p in _PROFILES.glob("*.json"))
        raise KeyError(f"unknown profile {profile_id!r}; known: {known}")
    return json.loads(path.read_text(encoding="utf-8"))


class Canvas:
    """Accumulates SVG elements for one profile."""

    def __init__(self, profile_id: str):
        self.profile = load_profile(profile_id)
        self.style = load_style()
        self.id = self.profile["id"]
        self.w = self.profile["width_px"]
        self.h = self.profile["height_px"]
        self.dpi = self.profile["dpi"]
        self.capacity_ml = self.profile.get("capacity_ml", 0)

        overlap_mm = self.profile.get("seam_overlap_mm", 0.0)
        overlap_px = overlap_mm / 25.4 * self.dpi
        self.x0 = overlap_px
        self.x1 = self.w - overlap_px
        self.y0 = 0.0
        self.y1 = float(self.h)
        self.pw = self.x1 - self.x0
        self.ph = self.y1 - self.y0

        self.scale = min(self.pw / REF_W, self.ph / REF_H)
        self.aspect = self.ph / self.pw

        strokes = self.style["stroke_px_at_9000"]
        self.HEAVY = self.s(strokes["heavy"])
        self.MED = self.s(strokes["medium"])
        self.LIGHT = self.s(strokes["light"])
        self.HAIR = max(2.0, self.s(strokes["hair"]))

        self.parts: list[str] = []
        self._group_depth = 0
        self._transformed: set[int] = set()

    # -- coordinates ---------------------------------------------------
    def nx(self, u: float) -> float:
        """Normalised x (0..1 across the printable sector) to pixels."""
        return self.x0 + u * self.pw

    def ny(self, v: float) -> float:
        """Normalised y (0..1 down the label) to pixels."""
        return self.y0 + v * self.ph

    def s(self, size_at_reference: float) -> float:
        """Scale a decorative size authored against the reference canvas."""
        return size_at_reference * self.scale

    def mm(self, millimetres: float) -> float:
        """Absolute millimetres to pixels at this profile's DPI."""
        return millimetres / 25.4 * self.dpi

    @property
    def band(self) -> str:
        """Which responsive arrangement this profile falls into."""
        if self.aspect < 0.40:
            return "short"
        if self.aspect < 0.65:
            return "medium"
        return "tall"

    # -- text metrics --------------------------------------------------
    @staticmethod
    def est_width(text: str, size: float, weight: str = "400",
                  family: str = "Inter", ls: float = 0.0) -> float:
        """Approximate rendered width. Good enough to prevent overflow.

        Avoids a font-metrics dependency; the constants are averages measured
        against the families this project uses.
        """
        if family.startswith("TeX"):
            k = 0.46
        elif weight in ("700", "800", "900"):
            k = 0.62
        else:
            k = 0.55
        return len(text) * size * k + max(len(text) - 1, 0) * ls

    @classmethod
    def fit_size(cls, text: str, max_width: float, size: float,
                 weight: str = "400", family: str = "Inter",
                 ls: float = 0.0) -> float:
        """Shrink ``size`` until ``text`` fits ``max_width``."""
        if max_width <= 0 or not text:
            return size
        w = cls.est_width(text, size, weight, family, ls)
        return size * (max_width / w) if w > max_width else size

    # -- primitives ----------------------------------------------------
    def add(self, element: str) -> None:
        if self._group_depth:
            self._transformed.add(len(self.parts))
        self.parts.append(element)

    @staticmethod
    def esc(text: str) -> str:
        return (text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;"))

    def text(self, x: float, y: float, s: str, size: float, *,
             family: str = "Inter", weight: str = "400", anchor: str = "middle",
             ls: float = 0.0, style: str = "") -> None:
        st = f' font-style="{style}"' if style else ""
        self.add(
            f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" '
            f'font-size="{size:.1f}" font-weight="{weight}" '
            f'letter-spacing="{ls:.1f}" text-anchor="{anchor}" '
            f'fill="{BLACK}"{st}>{self.esc(s)}</text>')

    def line(self, x1: float, y1: float, x2: float, y2: float,
             w: float | None = None, cap: str = "round") -> None:
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" '
                 f'y2="{y2:.1f}" stroke="{BLACK}" '
                 f'stroke-width="{w if w is not None else self.MED:.1f}" '
                 f'stroke-linecap="{cap}"/>')

    def circle(self, cx: float, cy: float, r: float,
               w: float | None = None, fill: str = "none") -> None:
        self.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" '
                 f'fill="{fill}" stroke="{BLACK}" '
                 f'stroke-width="{w if w is not None else self.MED:.1f}"/>')

    def dot(self, cx: float, cy: float, r: float) -> None:
        self.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{BLACK}"/>')

    def ellipse(self, cx: float, cy: float, rx: float, ry: float,
                w: float | None = None, fill: str = "none") -> None:
        self.add(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" '
                 f'ry="{ry:.1f}" fill="{fill}" stroke="{BLACK}" '
                 f'stroke-width="{w if w is not None else self.MED:.1f}"/>')

    def rect(self, x: float, y: float, w_: float, h_: float,
             w: float | None = None, fill: str = "none", rx: float = 0) -> None:
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w_:.1f}" '
                 f'height="{h_:.1f}" rx="{rx:.1f}" fill="{fill}" '
                 f'stroke="{BLACK}" stroke-width="{w if w is not None else self.MED:.1f}"/>')

    def path(self, d: str, w: float | None = None, fill: str = "none") -> None:
        self.add(f'<path d="{d}" fill="{fill}" stroke="{BLACK}" '
                 f'stroke-width="{w if w is not None else self.MED:.1f}" '
                 f'stroke-linecap="round" stroke-linejoin="round"/>')

    def filled(self, d: str) -> None:
        self.add(f'<path d="{d}" fill="{BLACK}" stroke="none"/>')

    def group(self, transform: str) -> "_Group":
        return _Group(self, transform)

    # -- composed shapes -----------------------------------------------
    def dotted_ring(self, cx: float, cy: float, r: float, n: int,
                    rd: float) -> None:
        for i in range(n):
            a = 2 * math.pi * i / n
            self.dot(cx + r * math.cos(a), cy + r * math.sin(a), rd)

    def star(self, cx: float, cy: float, r: float) -> None:
        pts = []
        for i in range(10):
            a = -math.pi / 2 + math.pi * i / 5
            rr = r if i % 2 == 0 else r * 0.42
            pts.append(f"{cx + rr*math.cos(a):.1f} {cy + rr*math.sin(a):.1f}")
        self.filled("M " + " L ".join(pts) + " Z")

    def heart(self, cx: float, cy: float, s: float) -> None:
        self.filled(
            f"M {cx:.1f} {cy+0.62*s:.1f} C {cx-0.95*s:.1f} {cy-0.08*s:.1f} "
            f"{cx-0.52*s:.1f} {cy-0.80*s:.1f} {cx:.1f} {cy-0.30*s:.1f} "
            f"C {cx+0.52*s:.1f} {cy-0.80*s:.1f} {cx+0.95*s:.1f} {cy-0.08*s:.1f} "
            f"{cx:.1f} {cy+0.62*s:.1f} Z")

    def heart_outline(self, cx: float, cy: float, s: float,
                      w: float | None = None) -> None:
        self.path(
            f"M {cx:.1f} {cy+0.62*s:.1f} C {cx-0.95*s:.1f} {cy-0.08*s:.1f} "
            f"{cx-0.52*s:.1f} {cy-0.80*s:.1f} {cx:.1f} {cy-0.30*s:.1f} "
            f"C {cx+0.52*s:.1f} {cy-0.80*s:.1f} {cx+0.95*s:.1f} {cy-0.08*s:.1f} "
            f"{cx:.1f} {cy+0.62*s:.1f} Z", w)

    # -- output --------------------------------------------------------
    def to_svg(self) -> str:
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{self.w}" height="{self.h}" '
            f'viewBox="0 0 {self.w} {self.h}">\n'
            f'<rect x="0" y="0" width="{self.w}" height="{self.h}" fill="#FFFFFF"/>\n'
            + "\n".join(self.parts) + "\n</svg>\n")

    def overflows_printable(self) -> bool:
        """Cheap guard: did anything get placed outside the seam-safe area?

        Checks explicit x coordinates of untransformed elements only. Content
        inside a ``group()`` is skipped because its coordinates are in the
        group's own space and are not comparable. For an authoritative check,
        rasterise and measure the ink bounds.
        """
        import re
        for i, part in enumerate(self.parts):
            if i in self._transformed:
                continue
            for match in re.finditer(r'(?:\bx|x1|x2|cx)="(-?[\d.]+)"', part):
                x = float(match.group(1))
                if x < self.x0 - 1 or x > self.x1 + 1:
                    return True
        return False


class _Group:
    def __init__(self, canvas: Canvas, transform: str):
        self.canvas = canvas
        self.transform = transform

    def __enter__(self) -> Canvas:
        self.canvas.add(f'<g transform="{self.transform}">')
        self.canvas._group_depth += 1
        return self.canvas

    def __exit__(self, *exc: object) -> None:
        self.canvas._group_depth -= 1
        self.canvas.add("</g>")
