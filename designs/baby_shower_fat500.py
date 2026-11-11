"""Baby Shower (boy vs girl) wrap for the FAT 500 ml profile.

A worked example of a real, non-mock design: deterministic vector artwork
built from the canvas spec in ``profiles/``. Run it directly to emit the SVG
master, and optionally the 1200 DPI PNG and physical-size PDF.

    python -m designs.baby_shower_fat500 --outdir output --raster

Canvas dimensions are read from the profile, never hardcoded, so repointing
PROFILE_ID at another profile reflows the same artwork to that canvas.
"""
from __future__ import annotations
import argparse, json, math, random
from pathlib import Path

PROFILE_ID = "fat_500ml"
_PROFILES = Path(__file__).resolve().parent.parent / "profiles"
_prof = json.loads((_PROFILES / f"{PROFILE_ID}.json").read_text(encoding="utf-8"))

W, H, DPI = _prof["width_px"], _prof["height_px"], _prof["dpi"]
BLACK = "#000000"
HEAVY, MED, LIGHT, HAIR = 26, 16, 11, 7


parts: list[str] = []
def add(s: str) -> None: parts.append(s)
def esc(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def text(x, y, s, size, *, family="Inter", weight="400", anchor="middle",
         ls=0, style="", fill=BLACK):
    st = f' font-style="{style}"' if style else ""
    add(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-size="{size:.1f}" '
        f'font-weight="{weight}" letter-spacing="{ls:.1f}" text-anchor="{anchor}" '
        f'fill="{fill}"{st}>{esc(s)}</text>')

def line(x1, y1, x2, y2, w=MED, cap="round"):
    add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
        f'stroke="{BLACK}" stroke-width="{w}" stroke-linecap="{cap}"/>')

def circle(cx, cy, r, w=MED, fill="none"):
    add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
        f'stroke="{BLACK}" stroke-width="{w}"/>')

def dot(cx, cy, r): add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{BLACK}"/>')

def ellipse(cx, cy, rx, ry, w=MED, fill="none", rot=None):
    tr = f' transform="rotate({rot} {cx:.1f} {cy:.1f})"' if rot else ""
    add(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{fill}" '
        f'stroke="{BLACK}" stroke-width="{w}"{tr}/>')

def path(d, w=MED, fill="none", cap="round", join="round"):
    add(f'<path d="{d}" fill="{fill}" stroke="{BLACK}" stroke-width="{w}" '
        f'stroke-linecap="{cap}" stroke-linejoin="{join}"/>')

def filled(d): add(f'<path d="{d}" fill="{BLACK}" stroke="none"/>')

def rect(x, y, w_, h_, w=MED, fill="none", rx=0):
    add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w_:.1f}" height="{h_:.1f}" rx="{rx}" '
        f'fill="{fill}" stroke="{BLACK}" stroke-width="{w}"/>')

def dotted_ring(cx, cy, r, n, rd, start=0.0):
    for i in range(n):
        a = start + 2 * math.pi * i / n
        dot(cx + r * math.cos(a), cy + r * math.sin(a), rd)

def star(cx, cy, r):
    d = []
    for i in range(10):
        a = -math.pi / 2 + math.pi * i / 5
        rr = r if i % 2 == 0 else r * 0.42
        d.append(f"{cx + rr*math.cos(a):.1f} {cy + rr*math.sin(a):.1f}")
    filled("M " + " L ".join(d) + " Z")

def heart(cx, cy, s):
    filled(f"M {cx:.1f} {cy+0.62*s:.1f} C {cx-0.95*s:.1f} {cy-0.08*s:.1f} "
           f"{cx-0.52*s:.1f} {cy-0.80*s:.1f} {cx:.1f} {cy-0.30*s:.1f} "
           f"C {cx+0.52*s:.1f} {cy-0.80*s:.1f} {cx+0.95*s:.1f} {cy-0.08*s:.1f} "
           f"{cx:.1f} {cy+0.62*s:.1f} Z")

def heart_outline(cx, cy, s, w=MED):
    path(f"M {cx:.1f} {cy+0.62*s:.1f} C {cx-0.95*s:.1f} {cy-0.08*s:.1f} "
         f"{cx-0.52*s:.1f} {cy-0.80*s:.1f} {cx:.1f} {cy-0.30*s:.1f} "
         f"C {cx+0.52*s:.1f} {cy-0.80*s:.1f} {cx+0.95*s:.1f} {cy-0.08*s:.1f} "
         f"{cx:.1f} {cy+0.62*s:.1f} Z", w)

# ---------------------------------------------------------------- motifs
def pacifier(cx, cy, s, w=MED):
    circle(cx, cy - 0.95 * s, 0.33 * s, w)                       # handle ring
    line(cx, cy - 0.62 * s, cx, cy - 0.50 * s, w)
    ellipse(cx, cy - 0.08 * s, 0.86 * s, 0.46 * s, w)            # shield
    dot(cx - 0.52 * s, cy - 0.08 * s, 0.075 * s)
    dot(cx + 0.52 * s, cy - 0.08 * s, 0.075 * s)
    path(f"M {cx-0.30*s:.1f} {cy+0.34*s:.1f} "
         f"C {cx-0.38*s:.1f} {cy+0.86*s:.1f} {cx+0.38*s:.1f} {cy+0.86*s:.1f} "
         f"{cx+0.30*s:.1f} {cy+0.34*s:.1f}", w)                  # teat

def baby_bottle(cx, cy, s, w=MED):
    path(f"M {cx-0.17*s:.1f} {cy-0.98*s:.1f} q {0.17*s:.1f} {-0.30*s:.1f} {0.34*s:.1f} {0:.1f} "
         f"l {0:.1f} {0.22*s:.1f} l {-0.34*s:.1f} {0:.1f} Z", w)        # teat
    rect(cx - 0.34 * s, cy - 0.76 * s, 0.68 * s, 0.20 * s, w, rx=14)    # collar
    path(f"M {cx-0.46*s:.1f} {cy-0.52*s:.1f} l {0.92*s:.1f} {0:.1f} "
         f"l {0:.1f} {1.02*s:.1f} q {0:.1f} {0.34*s:.1f} {-0.30*s:.1f} {0.34*s:.1f} "
         f"l {-0.32*s:.1f} {0:.1f} q {-0.30*s:.1f} {0:.1f} {-0.30*s:.1f} {-0.34*s:.1f} Z", w)
    for i, ty in enumerate((-0.22, 0.04, 0.30)):
        line(cx + 0.46 * s - 0.26 * s, cy + ty * s, cx + 0.46 * s - 0.06 * s, cy + ty * s, HAIR)

def rattle(cx, cy, s, w=MED):
    circle(cx, cy - 0.38 * s, 0.56 * s, w)
    for i in range(6):
        a = 2 * math.pi * i / 6 + 0.4
        dot(cx + 0.31 * s * math.cos(a), cy - 0.38 * s + 0.31 * s * math.sin(a), 0.075 * s)
    rect(cx - 0.115 * s, cy + 0.18 * s, 0.23 * s, 0.62 * s, w, rx=22)
    rect(cx - 0.30 * s, cy + 0.80 * s, 0.60 * s, 0.17 * s, w, rx=22)

def moon_stars(cx, cy, s, w=MED):
    path(f"M {cx+0.14*s:.1f} {cy-0.82*s:.1f} A {0.82*s:.1f} {0.82*s:.1f} 0 1 0 "
         f"{cx+0.14*s:.1f} {cy+0.82*s:.1f} A {0.66*s:.1f} {0.66*s:.1f} 0 1 1 "
         f"{cx+0.14*s:.1f} {cy-0.82*s:.1f} Z", w)
    for sx, sy, ss in ((0.74, -0.52, 0.17), (1.00, 0.14, 0.12), (0.62, 0.66, 0.14)):
        star(cx + sx * s, cy + sy * s, ss * s)

def bow_tie(cx, cy, s, w=MED):
    path(f"M {cx-0.17*s:.1f} {cy:.1f} L {cx-1.00*s:.1f} {cy-0.56*s:.1f} "
         f"L {cx-1.00*s:.1f} {cy+0.56*s:.1f} Z", w)
    path(f"M {cx+0.17*s:.1f} {cy:.1f} L {cx+1.00*s:.1f} {cy-0.56*s:.1f} "
         f"L {cx+1.00*s:.1f} {cy+0.56*s:.1f} Z", w)
    rect(cx - 0.19 * s, cy - 0.29 * s, 0.38 * s, 0.58 * s, w, rx=14)

def mustache(cx, cy, s):
    filled(f"M {cx:.1f} {cy+0.10*s:.1f} "
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

def hair_bow(cx, cy, s, w=MED):
    path(f"M {cx-0.15*s:.1f} {cy:.1f} C {cx-0.68*s:.1f} {cy-0.72*s:.1f} "
         f"{cx-1.18*s:.1f} {cy-0.38*s:.1f} {cx-1.03*s:.1f} {cy+0.06*s:.1f} "
         f"C {cx-0.93*s:.1f} {cy+0.44*s:.1f} {cx-0.44*s:.1f} {cy+0.36*s:.1f} {cx-0.15*s:.1f} {cy:.1f} Z", w)
    path(f"M {cx+0.15*s:.1f} {cy:.1f} C {cx+0.68*s:.1f} {cy-0.72*s:.1f} "
         f"{cx+1.18*s:.1f} {cy-0.38*s:.1f} {cx+1.03*s:.1f} {cy+0.06*s:.1f} "
         f"C {cx+0.93*s:.1f} {cy+0.44*s:.1f} {cx+0.44*s:.1f} {cy+0.36*s:.1f} {cx+0.15*s:.1f} {cy:.1f} Z", w)
    circle(cx, cy, 0.18 * s, w)
    path(f"M {cx-0.09*s:.1f} {cy+0.17*s:.1f} C {cx-0.26*s:.1f} {cy+0.62*s:.1f} "
         f"{cx-0.36*s:.1f} {cy+0.80*s:.1f} {cx-0.50*s:.1f} {cy+0.96*s:.1f}", w)
    path(f"M {cx+0.09*s:.1f} {cy+0.17*s:.1f} C {cx+0.26*s:.1f} {cy+0.62*s:.1f} "
         f"{cx+0.36*s:.1f} {cy+0.80*s:.1f} {cx+0.50*s:.1f} {cy+0.96*s:.1f}", w)

def eyelash_eye(cx, cy, s, w=MED):
    path(f"M {cx-s:.1f} {cy:.1f} Q {cx:.1f} {cy-0.80*s:.1f} {cx+s:.1f} {cy:.1f}", w)
    for k, ang in ((-0.98, 196), (-0.60, 224), (0.0, 262), (0.60, 300), (0.98, 344)):
        bx = cx + k * s
        by = cy - 0.60 * s * max(0.0, 1 - k * k) ** 0.5
        a = math.radians(ang)
        line(bx, by, bx + 0.44 * s * math.cos(a), by + 0.44 * s * math.sin(a), w)

def teddy(cx, cy, s, w=MED):
    for sx in (-1, 1):
        circle(cx + sx * 0.72 * s, cy - 0.66 * s, 0.30 * s, w)
        circle(cx + sx * 0.72 * s, cy - 0.66 * s, 0.15 * s, w)
    circle(cx, cy, 0.86 * s, w)
    ellipse(cx, cy + 0.33 * s, 0.45 * s, 0.33 * s, w)
    dot(cx - 0.30 * s, cy - 0.20 * s, 0.085 * s)
    dot(cx + 0.30 * s, cy - 0.20 * s, 0.085 * s)
    filled(f"M {cx-0.15*s:.1f} {cy+0.16*s:.1f} Q {cx:.1f} {cy+0.02*s:.1f} "
           f"{cx+0.15*s:.1f} {cy+0.16*s:.1f} Q {cx:.1f} {cy+0.31*s:.1f} {cx-0.15*s:.1f} {cy+0.16*s:.1f} Z")
    line(cx, cy + 0.31 * s, cx, cy + 0.44 * s, w)
    path(f"M {cx:.1f} {cy+0.44*s:.1f} Q {cx-0.18*s:.1f} {cy+0.60*s:.1f} {cx-0.27*s:.1f} {cy+0.43*s:.1f}", w)
    path(f"M {cx:.1f} {cy+0.44*s:.1f} Q {cx+0.18*s:.1f} {cy+0.60*s:.1f} {cx+0.27*s:.1f} {cy+0.43*s:.1f}", w)

def pram(cx, cy, s, w=MED):
    path(f"M {cx-0.95*s:.1f} {cy+0.18*s:.1f} A {0.95*s:.1f} {0.95*s:.1f} 0 0 0 "
         f"{cx+0.95*s:.1f} {cy+0.18*s:.1f} Z", w)
    path(f"M {cx-0.02*s:.1f} {cy+0.18*s:.1f} A {0.95*s:.1f} {0.95*s:.1f} 0 0 1 "
         f"{cx+0.95*s:.1f} {cy+0.18*s:.1f}", w)
    line(cx - 0.95 * s, cy + 0.18 * s, cx + 0.95 * s, cy + 0.18 * s, w)
    path(f"M {cx+0.95*s:.1f} {cy+0.18*s:.1f} L {cx+1.46*s:.1f} {cy-0.50*s:.1f}", w)
    path(f"M {cx+1.46*s:.1f} {cy-0.50*s:.1f} q {0.28*s:.1f} {-0.24*s:.1f} {0.46*s:.1f} {0.04*s:.1f}", w)
    for sx in (-1, 1):
        circle(cx + sx * 0.52 * s, cy + 0.76 * s, 0.30 * s, w)
        dot(cx + sx * 0.52 * s, cy + 0.76 * s, 0.07 * s)
        line(cx + sx * 0.52 * s, cy + 0.18 * s, cx + sx * 0.52 * s, cy + 0.46 * s, w)

def recycle(cx, cy, s, w=HEAVY):
    """Three chasing arrows, Mobius style."""
    for i in range(3):
        a = math.radians(90 + i * 120)
        add(f'<g transform="rotate({i*120} {cx:.1f} {cy:.1f})">')
        path(f"M {cx-0.62*s:.1f} {cy+0.36*s:.1f} L {cx-0.14*s:.1f} {cy-0.47*s:.1f}", w, cap="butt")
        filled(f"M {cx-0.14*s:.1f} {cy-0.62*s:.1f} L {cx+0.12*s:.1f} {cy-0.30*s:.1f} "
               f"L {cx-0.38*s:.1f} {cy-0.30*s:.1f} Z")
        add("</g>")
    del a

def bunting(x0, x1, y, sag, n, w=MED):
    """A hanging garland of triangular flags."""
    def yy(t): return y + sag * math.sin(math.pi * t)
    d = f"M {x0:.1f} {y:.1f} Q {(x0+x1)/2:.1f} {y+2*sag:.1f} {x1:.1f} {y:.1f}"
    path(d, LIGHT)
    for i in range(n):
        t = (i + 0.5) / n
        bx = x0 + (x1 - x0) * t
        by = yy(t)
        hw = (x1 - x0) / n * 0.34
        hgt = (x1 - x0) / n * 0.78
        if i % 2 == 0:
            path(f"M {bx-hw:.1f} {by:.1f} L {bx+hw:.1f} {by:.1f} L {bx:.1f} {by+hgt:.1f} Z", w)
        else:
            filled(f"M {bx-hw:.1f} {by:.1f} L {bx+hw:.1f} {by:.1f} L {bx:.1f} {by+hgt:.1f} Z")

def confetti(zones, seed=7):
    rng = random.Random(seed)
    for (x0, y0, x1, y1, n) in zones:
        for _ in range(n):
            x = rng.uniform(x0, x1); y = rng.uniform(y0, y1)
            k = rng.random()
            if k < 0.34: star(x, y, rng.uniform(26, 46))
            elif k < 0.67: heart(x, y, rng.uniform(26, 44))
            else: dot(x, y, rng.uniform(12, 22))


def build() -> str:
    """Return the complete SVG document for this design."""
    parts.clear()

    add(f'<rect x="0" y="0" width="{W}" height="{H}" fill="#FFFFFF"/>')

    # ---------------------------------------------------------- HERO (center)
    HX = 4300
    pacifier(HX, 430, 290, HEAVY)
    text(HX, 955, "WELCOME LITTLE ONE", 132, weight="600", ls=46)
    line(HX - 1300, 905, HX - 1180, 905, LIGHT)
    line(HX + 1180, 905, HX + 1300, 905, LIGHT)
    text(HX, 1540, "BABY SHOWER", 400, weight="900", ls=14)
    line(HX - 1480, 1670, HX + 1480, 1670, HEAVY)
    text(HX, 2075, "boy or girl?", 330, family="TeX Gyre Chorus", style="italic")
    for px, sz in ((-300, 46), (0, 68), (300, 46)):
        heart(HX + px, 2250, sz)

    # ------------------------------------------------- LEFT COLUMN (motifs)
    LX = 1480
    for cy_, fn in ((540, baby_bottle), (1390, rattle), (2240, moon_stars)):
        circle(LX, cy_, 330, MED)
        dotted_ring(LX, cy_, 400, 46, 11)
        fn(LX, cy_, 210, MED)

    # ------------------------------------------------ RIGHT BADGE (dotted)
    RX, RY, RR = 7180, 1330, 800
    dotted_ring(RX, RY, RR, 76, 17)
    pacifier(RX, RY - 500, 110, MED)
    text(RX, RY - 175, "Join us", 280, family="TeX Gyre Chorus", style="italic")
    text(RX, RY + 20, "TO CELEBRATE OUR", 120, weight="700", ls=16)
    text(RX, RY + 275, "little miracle", 250, family="TeX Gyre Chorus", style="italic")
    text(RX, RY + 450, "AND GUESS:", 112, weight="600", ls=12)
    text(RX, RY + 580, "HE OR SHE?", 112, weight="800", ls=12)
    for i in range(5):
        star(RX - 220 + i * 110, RY + 690, 38)

    # ------------------------------------------------------- MEDALLION ROW
    MY, MR = 3380, 620
    med_x = (1560, 3240, 4920, 6600)
    specs = (("pram", "LITTLE ONE"), ("boy", "TEAM BOY"),
             ("girl", "TEAM GIRL"), ("teddy", "BEST WISHES"))
    for cx_, (kind, cap) in zip(med_x, specs):
        circle(cx_, MY, MR, HEAVY)
        circle(cx_, MY, MR - 54, HAIR)
        if kind == "pram":
            pram(cx_, MY - 40, 330, MED)
        elif kind == "boy":
            mustache(cx_, MY - 170, 200)
            bow_tie(cx_, MY + 210, 230, MED)
        elif kind == "girl":
            eyelash_eye(cx_ - 160, MY - 215, 120, MED)
            eyelash_eye(cx_ + 160, MY - 215, 120, MED)
            hair_bow(cx_, MY + 180, 230, MED)
        else:
            teddy(cx_, MY - 20, 330, MED)
        text(cx_, MY + MR + 230, cap, 124, weight="800", ls=24)
        line(cx_ - 170, MY + MR + 300, cx_ + 170, MY + MR + 300, LIGHT)

    for gx in (2400, 4080, 5760):
        heart_outline(gx, MY, 62, LIGHT)

    # ------------------------------------------------------------- BUNTING
    bunting(900, 6150, 4400, 95, 11, MED)

    # ===================================================== FOOTER: NUTRITION
    NX, NY, NW, NH = 6260, 4400, 1520, 1500
    add(f'<rect x="{NX}" y="{NY}" width="{NW}" height="{NH}" fill="#FFFFFF" '
        f'stroke="{BLACK}" stroke-width="{MED}"/>')
    pad = 40
    cur = NY + 140
    text(NX + pad, cur, "Nutrition Facts", 130, weight="900", anchor="start")
    cur += 44; line(NX + pad, cur, NX + NW - pad, cur, HAIR); cur += 62
    text(NX + pad, cur, "Serving size 8fl oz (237 ml)", 62, anchor="start"); cur += 68
    text(NX + pad, cur, "Servings per container: about 2", 62, anchor="start"); cur += 30
    line(NX + pad, cur, NX + NW - pad, cur, 22); cur += 66
    text(NX + pad, cur, "Amount Per Serving", 62, weight="700", anchor="start"); cur += 72
    text(NX + pad, cur, "Calories", 66, weight="700", anchor="start")
    text(NX + pad + 290, cur, "0", 66, anchor="start"); cur += 24
    line(NX + pad, cur, NX + NW - pad, cur, HAIR); cur += 62
    text(NX + NW - pad, cur, "% Daily Value*", 58, weight="700", anchor="end"); cur += 18
    for nm, amt, off in (("Total fat", "0g", 300), ("Sodium", "0mg", 250),
                         ("Total carbohydrate", "0g", 690), ("Protein", "0g", 250)):
        line(NX + pad, cur, NX + NW - pad, cur, HAIR); cur += 68
        text(NX + pad, cur, nm, 62, weight="700", anchor="start")
        text(NX + pad + off, cur, amt, 62, anchor="start")
        text(NX + NW - pad, cur, "0%", 62, weight="700", anchor="end")
        cur += 14
    line(NX + pad, cur, NX + NW - pad, cur, 22); cur += 60
    text(NX + pad, cur, "Not a significant source of", 56, anchor="start"); cur += 60
    text(NX + pad, cur, "other nutrients.", 56, anchor="start"); cur += 24
    line(NX + pad, cur, NX + NW - pad, cur, HAIR); cur += 58
    text(NX + pad, cur, "*Percent Daily Values are based", 54, anchor="start"); cur += 56
    text(NX + pad, cur, "on a 2,000 calorie diet.", 54, anchor="start"); cur += 30
    line(NX + pad, cur, NX + NW - pad, cur, HAIR); cur += 58
    for ln in ("Ingredients: purified water treated with",
               "diverse stages of filtration, reverse",
               "osmosis and UV light and ozone sterilized."):
        text(NX + pad, cur, ln, 52, anchor="start"); cur += 56

    # rotated distributor block (placeholder copy)
    add(f'<g transform="translate({NX + NW + 95:.1f} {NY + NH:.1f}) rotate(-90)">')
    for i, ln in enumerate(("Distributed by: YOUR COMPANY LLC. (000) 000.0000",
                            "www.yourwebsite.com",
                            "Bottled by: YOUR BOTTLER, CITY, ST 00000 USA.")):
        add(f'<text x="0" y="{i*76:.1f}" font-family="Inter" font-size="58" '
            f'font-weight="{"700" if i == 0 else "400"}" text-anchor="start" '
            f'fill="{BLACK}">{esc(ln)}</text>')
    add("</g>")

    # ------------------------------------------------- FOOTER: CERT ICONS
    CY = 5240
    circle(1120, CY, 185, MED)
    heart_outline(1120, CY + 10, 150, LIGHT)
    text(1120, CY + 330, "BPA FREE", 88, weight="800", ls=10)
    recycle(2080, CY, 300, HEAVY)
    text(2080, CY + 330, "RECYCLABLE", 88, weight="800", ls=10)
    circle(3120, CY, 185, MED)
    star(3120, CY, 150)
    text(3120, CY + 330, "100% CARE", 88, weight="800", ls=10)

    # ---------------------------------------- FOOTER: SOCIAL + PRODUCT LINE
    SX, SY = 5020, 5200
    rect(SX - 330, SY - 78, 156, 156, LIGHT, rx=44)
    circle(SX - 252, SY, 44, LIGHT)
    dot(SX - 193, SY - 46, 14)
    text(SX, SY + 58, "f", 168, weight="900")
    circle(SX + 262, SY, 76, LIGHT)
    ellipse(SX + 262, SY, 32, 76, HAIR)
    line(SX + 186, SY, SX + 338, SY, HAIR)
    text(SX, SY + 290, "@YOURHANDLE", 130, weight="800", ls=16)
    line(SX - 1180, SY + 440, SX + 1180, SY + 440, LIGHT)
    text(SX, SY + 620, "PURIFIED WATER", 148, weight="800", ls=54)
    text(SX, SY + 752, "16.9 FL Oz / 0.5 L", 104, weight="500", ls=16)

    # ------------------------------------------ RIGHT VOID: vertical script
    add('<g transform="translate(7980 4180) rotate(-90)">')
    add(f'<text x="0" y="0" font-family="TeX Gyre Chorus" font-size="250" '
        f'font-style="italic" text-anchor="start" fill="{BLACK}">congratulations!</text>')
    add("</g>")
    for i, sy_ in enumerate((2500, 2680, 2860)):
        star(7760, sy_, 44 - i * 8)

    # ------------------------------------------------------------ CONFETTI
    confetti([
        (2620, 320, 2980, 2250, 6),      # between left column and hero
        (980, 5700, 3450, 5900, 5),      # bottom-left under cert icons
        (3900, 4990, 5900, 5120, 4),     # under bunting, above social
        (6450, 2200, 7850, 2420, 4),     # under the right badge
        (960, 2900, 1180, 3150, 2),      # tiny accent left edge
    ], seed=11)

    return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
            f'viewBox="0 0 {W} {H}">\n' + "\n".join(parts) + "\n</svg>\n")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--outdir", default="output")
    ap.add_argument("--raster", action="store_true",
                    help="also write the 1200 DPI PNG and physical-size PDF")
    a = ap.parse_args()
    out = Path(a.outdir); out.mkdir(parents=True, exist_ok=True)
    stem = f"babyshower_{PROFILE_ID}"
    svg_path = out / f"{stem}.svg"
    svg_path.write_text(build(), encoding="utf-8")
    print(f"SVG: {svg_path}")
    if a.raster:
        import cairosvg
        from PIL import Image
        Image.MAX_IMAGE_PIXELS = None
        tmp = out / "_tmp.png"
        cairosvg.svg2png(url=str(svg_path), write_to=str(tmp),
                         output_width=W, output_height=H)
        im = Image.open(tmp).convert("L")
        png_path = out / f"{stem}_{DPI}dpi.png"
        im.save(png_path, dpi=(DPI, DPI), optimize=True)
        tmp.unlink()
        # px -> pt at cairo's 96dpi default, scaled to true physical inches
        cairosvg.svg2pdf(url=str(svg_path), write_to=str(out / f"{stem}.pdf"),
                         scale=(W / DPI * 72) / (W * 72 / 96))
        print(f"PNG: {png_path}  ({W}x{H} @ {DPI} DPI)")
        print(f"PDF: {out / f'{stem}.pdf'}  "
              f"({_prof['physical_width_mm']} x {_prof['physical_height_mm']} mm)")


if __name__ == "__main__":
    main()
