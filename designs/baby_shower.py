"""Baby Shower (boy vs girl) — composes for any bottle profile.

The five profiles differ in aspect ratio by 2.5x, so one fixed composition
cannot serve them all: scaling a 7800x6000 layout into a 7800x2400 label would
overflow by a factor of two and a half. Instead the design picks an
*arrangement* by aspect band and places everything in normalised coordinates
inside the printable sector.

    tall    aspect >= 0.65   three bands: hero, medallion row, footer
    medium  0.40 - 0.65      two bands, no side column
    short   aspect < 0.40    a single horizontal strip

Run it:

    python -m designs.baby_shower --profile fat_500ml --outdir output --raster
    python -m designs.baby_shower --all --outdir output
"""
from __future__ import annotations

import argparse
from pathlib import Path

from designs import furniture, motifs
from designs.canvas import Canvas

DISTRIBUTOR = [
    "Distributed by: YOUR COMPANY LLC. (000) 000.0000",
    "www.yourwebsite.com",
    "Bottled by: YOUR BOTTLER, CITY, ST 00000 USA.",
]

MEDALLIONS = (("pram", "LITTLE ONE"), ("boy", "TEAM BOY"),
              ("girl", "TEAM GIRL"), ("teddy", "BEST WISHES"))


# ---------------------------------------------------------------- helpers
def _hero(c: Canvas, u: float, v: float, width_u: float, *,
          compact: bool = False) -> None:
    """Wordmark block centred on normalised ``(u, v)``."""
    cx = c.nx(u)
    span = c.pw * width_u
    title = c.fit_size("BABY SHOWER", span, span / 5.6, "900")
    if not compact:
        kicker = title * 0.33
        kicker_y = c.ny(v) - title * 1.25
        headroom = (kicker_y - kicker) - c.y0
        # pacifier occupies ~1.28x its size above centre, 0.86x below
        size = min(title * 0.72, max(0.0, headroom) / 1.5)
        if size > title * 0.22:
            motifs.pacifier(c, cx, c.y0 + headroom * 0.5, size, c.HEAVY)
        c.text(cx, kicker_y, "WELCOME LITTLE ONE",
               kicker, weight="600", ls=kicker * 0.35)
    c.text(cx, c.ny(v), "BABY SHOWER", title, weight="900", ls=title * 0.035)
    c.line(cx - span * 0.49, c.ny(v) + title * 0.33,
           cx + span * 0.49, c.ny(v) + title * 0.33, c.HEAVY)
    c.text(cx, c.ny(v) + title * 1.33, "boy or girl?", title * 0.82,
           family="TeX Gyre Chorus", style="italic")


def _badge(c: Canvas, u: float, v: float, r_u: float) -> None:
    """Dotted script roundel."""
    cx, cy = c.nx(u), c.ny(v)
    r = c.pw * r_u
    c.dotted_ring(cx, cy, r, 76, r * 0.021)
    motifs.pacifier(c, cx, cy - r * 0.62, r * 0.14, c.MED)
    c.text(cx, cy - r * 0.22, "Join us", r * 0.35,
           family="TeX Gyre Chorus", style="italic")
    c.text(cx, cy + r * 0.02, "TO CELEBRATE OUR", r * 0.15, weight="700",
           ls=r * 0.020)
    c.text(cx, cy + r * 0.34, "little miracle", r * 0.31,
           family="TeX Gyre Chorus", style="italic")
    c.text(cx, cy + r * 0.56, "AND GUESS:", r * 0.14, weight="600", ls=r * 0.015)
    c.text(cx, cy + r * 0.72, "HE OR SHE?", r * 0.14, weight="800", ls=r * 0.015)


def _medallion_row(c: Canvas, v: float, r_u: float, u0: float, u1: float,
                   kinds=MEDALLIONS, captions: bool = True) -> None:
    n = len(kinds)
    r = c.pw * r_u
    step = (u1 - u0) / max(n - 1, 1) if n > 1 else 0.0
    for i, (kind, cap) in enumerate(kinds):
        motifs.medallion(c, c.nx(u0 + i * step), c.ny(v), r, kind,
                         cap if captions else None)


def _panel_block(c: Canvas, v: float, w_mm: float, h_v: float, *,
                 right_u: float = 1.0, ingredients: bool = True) -> None:
    """Nutrition panel plus its rotated distributor block, as one unit.

    Anchored to ``right_u`` of the printable sector and laid out right to
    left, so the rotated text cannot drift into the seam overlap however the
    profile is shaped. Hand-positioning the panel and hoping the rotated block
    fits is exactly the mistake this avoids.
    """
    w = c.mm(w_mm)
    h = c.ph * h_v
    y = c.ny(v)

    gap = c.mm(2.0)
    dist_size = h * 0.035
    dist_w = len(DISTRIBUTOR) * dist_size * 1.30

    right = c.nx(right_u)
    x = right - dist_w - gap - w
    if x < c.x0:
        raise ValueError(
            f"{c.id}: nutrition block {(dist_w + gap + w)/c.pw:.0%} of the "
            "printable width does not fit")

    furniture.nutrition_panel(c, x, y, w, h, ingredients=ingredients)
    furniture.distributor_block(c, x + w + gap, y + h, h, DISTRIBUTOR)


# ------------------------------------------------------------ arrangements
def _compose_tall(c: Canvas) -> None:
    _hero(c, 0.44, 0.285, 0.42)

    for i, (vv, fn) in enumerate(((0.09, motifs.baby_bottle),
                                  (0.235, motifs.rattle),
                                  (0.380, motifs.moon_stars))):
        cx, cy = c.nx(0.085), c.ny(vv)
        rr = c.pw * 0.043
        c.circle(cx, cy, rr, c.MED)
        c.dotted_ring(cx, cy, rr * 1.21, 46, rr * 0.033)
        fn(c, cx, cy, rr * 0.64, c.MED)

    _badge(c, 0.850, 0.235, 0.104)
    _medallion_row(c, 0.585, 0.078, 0.088, 0.685)

    motifs.bunting(c, c.nx(0.01), c.nx(0.68), c.ny(0.760), c.ph * 0.014, 11)

    _panel_block(c, 0.700, 31.0, 0.265)

    furniture.cert_row(c, c.nx(0.055), c.ny(0.875), c.pw * 0.115, c.pw * 0.048)
    furniture.descriptor(c, c.nx(0.47), c.ny(0.955), "PURIFIED WATER",
                         furniture.volume_label(c), c.pw * 0.019)

    motifs.confetti(c, [(0.175, 0.04, 0.215, 0.30, 4),
                        (0.02, 0.955, 0.30, 0.99, 4),
                        (0.33, 0.395, 0.62, 0.425, 4),
                        (0.72, 0.40, 0.90, 0.46, 3)])


def _compose_medium(c: Canvas) -> None:
    _hero(c, 0.30, 0.265, 0.38)
    _badge(c, 0.850, 0.250, 0.112)
    _medallion_row(c, 0.545, 0.074, 0.085, 0.640)

    motifs.bunting(c, c.nx(0.02), c.nx(0.62), c.ny(0.755), c.ph * 0.013, 12)

    _panel_block(c, 0.505, 31.0, 0.455)

    furniture.cert_row(c, c.nx(0.060), c.ny(0.895), c.pw * 0.098, c.pw * 0.040)
    furniture.descriptor(c, c.nx(0.470), c.ny(0.930), "PURIFIED WATER",
                         furniture.volume_label(c), c.pw * 0.016)

    motifs.confetti(c, [(0.60, 0.03, 0.70, 0.11, 3),
                        (0.70, 0.38, 0.90, 0.44, 3)])


def _compose_short(c: Canvas) -> None:
    """One horizontal strip: wordmark, three medallions, panel."""
    _hero(c, 0.165, 0.42, 0.26, compact=True)

    _medallion_row(c, 0.47, 0.055, 0.395, 0.625,
                   kinds=(("boy", "TEAM BOY"), ("pram", "LITTLE ONE"),
                          ("girl", "TEAM GIRL")))

    _panel_block(c, 0.045, 27.0, 0.915, ingredients=False)

    furniture.cert_row(c, c.nx(0.050), c.ny(0.760), c.pw * 0.068, c.pw * 0.028)
    furniture.descriptor(c, c.nx(0.510), c.ny(0.880), "PURIFIED WATER",
                         furniture.volume_label(c), c.pw * 0.0125)

    motifs.confetti(c, [(0.31, 0.10, 0.36, 0.85, 4), (0.66, 0.10, 0.71, 0.85, 4)])


ARRANGEMENTS = {"tall": _compose_tall, "medium": _compose_medium,
                "short": _compose_short}


# ------------------------------------------------------------------- build
def build(profile_id: str) -> tuple[str, Canvas]:
    """Compose the design for ``profile_id``; returns the SVG and the canvas."""
    c = Canvas(profile_id)
    ARRANGEMENTS[c.band](c)
    return c.to_svg(), c


def write(profile_id: str, outdir: Path, raster: bool = False) -> dict[str, Path]:
    svg_text, c = build(profile_id)
    outdir.mkdir(parents=True, exist_ok=True)
    stem = f"babyshower_{profile_id}"
    written: dict[str, Path] = {}

    svg_path = outdir / f"{stem}.svg"
    svg_path.write_text(svg_text, encoding="utf-8")
    written["svg"] = svg_path

    if raster:
        import cairosvg
        from PIL import Image
        Image.MAX_IMAGE_PIXELS = None

        tmp = outdir / f"_{stem}.tmp.png"
        cairosvg.svg2png(url=str(svg_path), write_to=str(tmp),
                         output_width=c.w, output_height=c.h)
        png_path = outdir / f"{stem}_{c.dpi}dpi.png"
        Image.open(tmp).convert("L").save(png_path, dpi=(c.dpi, c.dpi),
                                          optimize=True)
        tmp.unlink()
        written["png"] = png_path

        pdf_path = outdir / f"{stem}.pdf"
        cairosvg.svg2pdf(url=str(svg_path), write_to=str(pdf_path),
                         scale=(c.w / c.dpi * 72) / (c.w * 72 / 96))
        written["pdf"] = pdf_path
    return written


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--profile", default="fat_500ml")
    ap.add_argument("--all", action="store_true", help="every profile")
    ap.add_argument("--outdir", type=Path, default=Path("output"))
    ap.add_argument("--raster", action="store_true")
    args = ap.parse_args()

    from designs.canvas import _PROFILES
    ids = (sorted(p.stem for p in _PROFILES.glob("*.json"))
           if args.all else [args.profile])
    for pid in ids:
        files = write(pid, args.outdir, args.raster)
        c = Canvas(pid)
        print(f"{pid:12s} band={c.band:6s} printable={int(c.pw)}x{int(c.ph)} "
              f"scale={c.scale:.2f}  -> {', '.join(p.name for p in files.values())}")


if __name__ == "__main__":
    main()
