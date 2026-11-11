"""Decorative motifs, drawn into a :class:`designs.canvas.Canvas`.

Every motif takes the canvas, a centre, and a size ``s`` expressed in pixels
on that canvas. Callers obtain ``s`` from ``canvas.s(...)`` so motifs scale
with the profile. Motifs never read the profile themselves.
"""
from __future__ import annotations

import math
import random

from designs.canvas import Canvas


def pacifier(c: Canvas, cx: float, cy: float, s: float, w: float) -> None:
    c.circle(cx, cy - 0.95 * s, 0.33 * s, w)
    c.line(cx, cy - 0.62 * s, cx, cy - 0.50 * s, w)
    c.ellipse(cx, cy - 0.08 * s, 0.86 * s, 0.46 * s, w)
    c.dot(cx - 0.52 * s, cy - 0.08 * s, 0.075 * s)
    c.dot(cx + 0.52 * s, cy - 0.08 * s, 0.075 * s)
    c.path(f"M {cx-0.30*s:.1f} {cy+0.34*s:.1f} "
           f"C {cx-0.38*s:.1f} {cy+0.86*s:.1f} {cx+0.38*s:.1f} {cy+0.86*s:.1f} "
           f"{cx+0.30*s:.1f} {cy+0.34*s:.1f}", w)


def baby_bottle(c: Canvas, cx: float, cy: float, s: float, w: float) -> None:
    c.path(f"M {cx-0.17*s:.1f} {cy-0.98*s:.1f} q {0.17*s:.1f} {-0.30*s:.1f} "
           f"{0.34*s:.1f} {0:.1f} l {0:.1f} {0.22*s:.1f} l {-0.34*s:.1f} {0:.1f} Z", w)
    c.rect(cx - 0.34 * s, cy - 0.76 * s, 0.68 * s, 0.20 * s, w, rx=0.05 * s)
    c.path(f"M {cx-0.46*s:.1f} {cy-0.52*s:.1f} l {0.92*s:.1f} {0:.1f} "
           f"l {0:.1f} {1.02*s:.1f} q {0:.1f} {0.34*s:.1f} {-0.30*s:.1f} {0.34*s:.1f} "
           f"l {-0.32*s:.1f} {0:.1f} q {-0.30*s:.1f} {0:.1f} {-0.30*s:.1f} {-0.34*s:.1f} Z", w)
    for ty in (-0.22, 0.04, 0.30):
        c.line(cx + 0.20 * s, cy + ty * s, cx + 0.40 * s, cy + ty * s, c.HAIR)


def rattle(c: Canvas, cx: float, cy: float, s: float, w: float) -> None:
    c.circle(cx, cy - 0.38 * s, 0.56 * s, w)
    for i in range(6):
        a = 2 * math.pi * i / 6 + 0.4
        c.dot(cx + 0.31 * s * math.cos(a), cy - 0.38 * s + 0.31 * s * math.sin(a),
              0.075 * s)
    c.rect(cx - 0.115 * s, cy + 0.18 * s, 0.23 * s, 0.62 * s, w, rx=0.08 * s)
    c.rect(cx - 0.30 * s, cy + 0.80 * s, 0.60 * s, 0.17 * s, w, rx=0.08 * s)


def moon_stars(c: Canvas, cx: float, cy: float, s: float, w: float) -> None:
    c.path(f"M {cx+0.14*s:.1f} {cy-0.82*s:.1f} A {0.82*s:.1f} {0.82*s:.1f} 0 1 0 "
           f"{cx+0.14*s:.1f} {cy+0.82*s:.1f} A {0.66*s:.1f} {0.66*s:.1f} 0 1 1 "
           f"{cx+0.14*s:.1f} {cy-0.82*s:.1f} Z", w)
    for sx, sy, ss in ((0.74, -0.52, 0.17), (1.00, 0.14, 0.12), (0.62, 0.66, 0.14)):
        c.star(cx + sx * s, cy + sy * s, ss * s)


def bow_tie(c: Canvas, cx: float, cy: float, s: float, w: float) -> None:
    c.path(f"M {cx-0.17*s:.1f} {cy:.1f} L {cx-1.00*s:.1f} {cy-0.56*s:.1f} "
           f"L {cx-1.00*s:.1f} {cy+0.56*s:.1f} Z", w)
    c.path(f"M {cx+0.17*s:.1f} {cy:.1f} L {cx+1.00*s:.1f} {cy-0.56*s:.1f} "
           f"L {cx+1.00*s:.1f} {cy+0.56*s:.1f} Z", w)
    c.rect(cx - 0.19 * s, cy - 0.29 * s, 0.38 * s, 0.58 * s, w, rx=0.05 * s)


def mustache(c: Canvas, cx: float, cy: float, s: float) -> None:
    c.filled(
        f"M {cx:.1f} {cy+0.10*s:.1f} "
        f"C {cx-0.22*s:.1f} {cy-0.16*s:.1f} {cx-0.52*s:.1f} {cy-0.34*s:.1f} {cx-0.86*s:.1f} {cy-0.30*s:.1f} "
        f"C {cx-1.20*s:.1f} {cy-0.26*s:.1f} {cx-1.36*s:.1f} {cy+0.02*s:.1f} {cx-1.30*s:.1f} {cy+0.14*s:.1f} "
        f"C {cx-1.24*s:.1f} {cy+0.02*s:.1f} {cx-1.02*s:.1f} {cy-0.06*s:.1f} {cx-0.80*s:.1f} {cy+0.04*s:.1f} "
        f"C {cx-0.56*s:.1f} {cy+0.16*s:.1f} {cx-0.44*s:.1f} {cy+0.42*s:.1f} {cx-0.20*s:.1f} {cy+0.42*s:.1f} "
        f"C {cx-0.08*s:.1f} {cy+0.42*s:.1f} {cx-0.03*s:.1f} {cy+0.32*s:.1f} {cx:.1f} {cy+0.24*s:.1f} "
        f"C {cx+0.03*s:.1f} {cy+0.32*s:.1f} {cx+0.08*s:.1f} {cy+0.42*s:.1f} {cx+0.20*s:.1f} {cy+0.42*s:.1f} "
        f"C {cx+0.44*s:.1f} {cy+0.42*s:.1f} {cx+0.56*s:.1f} {cy+0.16*s:.1f} {cx+0.80*s:.1f} {cy+0.04*s:.1f} "
        f"C {cx+1.02*s:.1f} {cy-0.06*s:.1f} {cx+1.24*s:.1f} {cy+0.02*s:.1f} {cx+1.30*s:.1f} {cy+0.14*s:.1f} "
        f"C {cx+1.36*s:.1f} {cy+0.02*s:.1f} {cx+1.20*s:.1f} {cy-0.26*s:.1f} {cx+0.86*s:.1f} {cy-0.30*s:.1f} "
        f"C {cx+0.52*s:.1f} {cy-0.34*s:.1f} {cx+0.22*s:.1f} {cy-0.16*s:.1f} {cx:.1f} {cy+0.10*s:.1f} Z")


def hair_bow(c: Canvas, cx: float, cy: float, s: float, w: float) -> None:
    for sign in (-1, 1):
        c.path(
            f"M {cx+sign*0.15*s:.1f} {cy:.1f} "
            f"C {cx+sign*0.68*s:.1f} {cy-0.72*s:.1f} {cx+sign*1.18*s:.1f} {cy-0.38*s:.1f} "
            f"{cx+sign*1.03*s:.1f} {cy+0.06*s:.1f} "
            f"C {cx+sign*0.93*s:.1f} {cy+0.44*s:.1f} {cx+sign*0.44*s:.1f} {cy+0.36*s:.1f} "
            f"{cx+sign*0.15*s:.1f} {cy:.1f} Z", w)
    c.circle(cx, cy, 0.18 * s, w)
    for sign in (-1, 1):
        c.path(f"M {cx+sign*0.09*s:.1f} {cy+0.17*s:.1f} "
               f"C {cx+sign*0.26*s:.1f} {cy+0.62*s:.1f} {cx+sign*0.36*s:.1f} {cy+0.80*s:.1f} "
               f"{cx+sign*0.50*s:.1f} {cy+0.96*s:.1f}", w)


def eyelash_eye(c: Canvas, cx: float, cy: float, s: float, w: float) -> None:
    c.path(f"M {cx-s:.1f} {cy:.1f} Q {cx:.1f} {cy-0.80*s:.1f} {cx+s:.1f} {cy:.1f}", w)
    for k, ang in ((-0.98, 196), (-0.60, 224), (0.0, 262), (0.60, 300), (0.98, 344)):
        bx = cx + k * s
        by = cy - 0.60 * s * max(0.0, 1 - k * k) ** 0.5
        a = math.radians(ang)
        c.line(bx, by, bx + 0.44 * s * math.cos(a), by + 0.44 * s * math.sin(a), w)


def teddy(c: Canvas, cx: float, cy: float, s: float, w: float) -> None:
    for sx in (-1, 1):
        c.circle(cx + sx * 0.72 * s, cy - 0.66 * s, 0.30 * s, w)
        c.circle(cx + sx * 0.72 * s, cy - 0.66 * s, 0.15 * s, w)
    c.circle(cx, cy, 0.86 * s, w)
    c.ellipse(cx, cy + 0.33 * s, 0.45 * s, 0.33 * s, w)
    c.dot(cx - 0.30 * s, cy - 0.20 * s, 0.085 * s)
    c.dot(cx + 0.30 * s, cy - 0.20 * s, 0.085 * s)
    c.filled(f"M {cx-0.15*s:.1f} {cy+0.16*s:.1f} Q {cx:.1f} {cy+0.02*s:.1f} "
             f"{cx+0.15*s:.1f} {cy+0.16*s:.1f} Q {cx:.1f} {cy+0.31*s:.1f} "
             f"{cx-0.15*s:.1f} {cy+0.16*s:.1f} Z")
    c.line(cx, cy + 0.31 * s, cx, cy + 0.44 * s, w)
    for sign in (-1, 1):
        c.path(f"M {cx:.1f} {cy+0.44*s:.1f} Q {cx+sign*0.18*s:.1f} {cy+0.60*s:.1f} "
               f"{cx+sign*0.27*s:.1f} {cy+0.43*s:.1f}", w)


def pram(c: Canvas, cx: float, cy: float, s: float, w: float) -> None:
    c.path(f"M {cx-0.95*s:.1f} {cy+0.18*s:.1f} A {0.95*s:.1f} {0.95*s:.1f} 0 0 0 "
           f"{cx+0.95*s:.1f} {cy+0.18*s:.1f} Z", w)
    c.path(f"M {cx-0.02*s:.1f} {cy+0.18*s:.1f} A {0.95*s:.1f} {0.95*s:.1f} 0 0 1 "
           f"{cx+0.95*s:.1f} {cy+0.18*s:.1f}", w)
    c.line(cx - 0.95 * s, cy + 0.18 * s, cx + 0.95 * s, cy + 0.18 * s, w)
    c.path(f"M {cx+0.95*s:.1f} {cy+0.18*s:.1f} L {cx+1.46*s:.1f} {cy-0.50*s:.1f}", w)
    c.path(f"M {cx+1.46*s:.1f} {cy-0.50*s:.1f} q {0.28*s:.1f} {-0.24*s:.1f} "
           f"{0.46*s:.1f} {0.04*s:.1f}", w)
    for sx in (-1, 1):
        c.circle(cx + sx * 0.52 * s, cy + 0.76 * s, 0.30 * s, w)
        c.dot(cx + sx * 0.52 * s, cy + 0.76 * s, 0.07 * s)
        c.line(cx + sx * 0.52 * s, cy + 0.18 * s, cx + sx * 0.52 * s, cy + 0.46 * s, w)


MEDALLION_ART = {
    "pram": lambda c, cx, cy, r: pram(c, cx, cy - 0.06 * r, 0.52 * r, c.MED),
    "boy": lambda c, cx, cy, r: (mustache(c, cx, cy - 0.27 * r, 0.32 * r),
                                 bow_tie(c, cx, cy + 0.33 * r, 0.36 * r, c.MED)),
    "girl": lambda c, cx, cy, r: (eyelash_eye(c, cx - 0.25 * r, cy - 0.34 * r, 0.19 * r, c.MED),
                                  eyelash_eye(c, cx + 0.25 * r, cy - 0.34 * r, 0.19 * r, c.MED),
                                  hair_bow(c, cx, cy + 0.28 * r, 0.36 * r, c.MED)),
    "teddy": lambda c, cx, cy, r: teddy(c, cx, cy - 0.03 * r, 0.52 * r, c.MED),
}


def medallion(c: Canvas, cx: float, cy: float, r: float, kind: str,
              caption: str | None = None) -> None:
    """A ringed circular motif with an optional caption beneath."""
    if kind not in MEDALLION_ART:
        raise KeyError(f"unknown medallion {kind!r}; known: {sorted(MEDALLION_ART)}")
    c.circle(cx, cy, r, c.HEAVY)
    c.circle(cx, cy, r - c.s(54), c.HAIR)
    MEDALLION_ART[kind](c, cx, cy, r)
    if caption:
        size = r * 0.20
        c.text(cx, cy + r + size * 1.5, caption, size, weight="800", ls=size * 0.19)
        c.line(cx - r * 0.27, cy + r + size * 2.1, cx + r * 0.27,
               cy + r + size * 2.1, c.LIGHT)


def bunting(c: Canvas, x0: float, x1: float, y: float, sag: float,
            n: int) -> None:
    """A hanging garland of alternating filled and outlined flags."""
    c.path(f"M {x0:.1f} {y:.1f} Q {(x0+x1)/2:.1f} {y+2*sag:.1f} {x1:.1f} {y:.1f}",
           c.LIGHT)
    for i in range(n):
        t = (i + 0.5) / n
        bx = x0 + (x1 - x0) * t
        by = y + sag * math.sin(math.pi * t)
        hw = (x1 - x0) / n * 0.34
        hgt = (x1 - x0) / n * 0.78
        d = (f"M {bx-hw:.1f} {by:.1f} L {bx+hw:.1f} {by:.1f} "
             f"L {bx:.1f} {by+hgt:.1f} Z")
        c.path(d, c.MED) if i % 2 == 0 else c.filled(d)


def confetti(c: Canvas, zones: list[tuple[float, float, float, float, int]],
             seed: int = 11) -> None:
    """Scatter small marks in normalised rectangles ``(u0, v0, u1, v1, n)``."""
    rng = random.Random(seed)
    for u0, v0, u1, v1, n in zones:
        for _ in range(n):
            x = c.nx(rng.uniform(u0, u1))
            y = c.ny(rng.uniform(v0, v1))
            k = rng.random()
            if k < 0.34:
                c.star(x, y, c.s(rng.uniform(26, 46)))
            elif k < 0.67:
                c.heart(x, y, c.s(rng.uniform(26, 44)))
            else:
                c.dot(x, y, c.s(rng.uniform(12, 22)))
