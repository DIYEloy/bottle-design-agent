"""Regulatory and brand furniture: the parts that repeat on every bottle.

Unlike motifs, furniture is sized in millimetres rather than scaled with the
canvas, because legibility does not scale. The nutrition panel is laid out to
fit whatever box it is given, deriving its leading and type size from the box
height, so the same call works on a 127 mm tall label and a 50 mm one.

Serving count is derived from the profile's capacity, never copied: the
supplied masters show 'about 1' at 250 ml and 'about 2' at 500 ml.
"""
from __future__ import annotations

from designs.canvas import Canvas
from engine.components import servings_for_capacity

#: Relative row heights for the nutrition panel, in layout units.
#: ``rule`` entries draw a separator of the given weight.
_PANEL_ROWS: list[tuple[str, float, object]] = [
    ("title", 2.00, "Nutrition Facts"),
    ("rule", 0.30, "hair"),
    ("line", 0.95, "Serving size 8fl oz (237 ml)"),
    ("line", 0.95, "__SERVINGS__"),
    ("rule", 0.40, "thick"),
    ("bold", 0.95, "Amount Per Serving"),
    ("calories", 1.00, ("Calories", "0")),
    ("rule", 0.30, "hair"),
    ("right", 0.90, "% Daily Value*"),
    ("nutrient", 1.00, ("Total fat", "0g", "0%")),
    ("nutrient", 1.00, ("Sodium", "0mg", "0%")),
    ("nutrient", 1.00, ("Total carbohydrate", "0g", "0%")),
    ("nutrient", 1.00, ("Protein", "0g", "0%")),
    ("rule", 0.40, "thick"),
    ("small", 0.85, "Not a significant source of"),
    ("small", 0.85, "other nutrients."),
    ("rule", 0.30, "hair"),
    ("small", 0.80, "*Percent Daily Values are based"),
    ("small", 0.80, "on a 2,000 calorie diet."),
]


def nutrition_panel(c: Canvas, x: float, y: float, w: float, h: float, *,
                    ingredients: bool = True) -> None:
    """Draw the FDA panel fitted to the box ``(x, y, w, h)``."""
    rows = list(_PANEL_ROWS)
    if ingredients:
        rows += [
            ("rule", 0.30, "hair"),
            ("small", 0.80, "Ingredients: purified water treated"),
            ("small", 0.80, "with diverse stages of filtration,"),
            ("small", 0.80, "reverse osmosis and UV light and"),
            ("small", 0.80, "ozone sterilized."),
        ]

    servings = servings_for_capacity(c.capacity_ml or 500)
    total_units = sum(r[1] for r in rows)
    pad = w * 0.028
    unit = (h - 2 * pad) / total_units
    inner = w - 2 * pad

    c.rect(x, y, w, h, c.MED, fill="#FFFFFF")

    cur = y + pad
    for kind, weight, payload in rows:
        span = unit * weight
        if kind == "rule":
            thickness = c.HAIR if payload == "hair" else max(c.HAIR * 2.4, c.MED)
            c.line(x + pad, cur + span * 0.5, x + w - pad, cur + span * 0.5,
                   thickness, cap="butt")
            cur += span
            continue

        baseline = cur + span * 0.82
        if kind == "title":
            size = c.fit_size(str(payload), inner, span * 0.80, "900")
            c.text(x + pad, baseline, str(payload), size,
                   weight="900", anchor="start")
        elif kind == "line":
            text = (f"Servings per container: {servings}"
                    if payload == "__SERVINGS__" else str(payload))
            size = c.fit_size(text, inner, span * 0.62)
            c.text(x + pad, baseline, text, size, anchor="start")
        elif kind == "bold":
            size = c.fit_size(str(payload), inner, span * 0.62, "700")
            c.text(x + pad, baseline, str(payload), size,
                   weight="700", anchor="start")
        elif kind == "calories":
            name, value = payload
            size = c.fit_size(f"{name}  {value}", inner * 0.6, span * 0.68, "700")
            c.text(x + pad, baseline, name, size, weight="700", anchor="start")
            c.text(x + pad + c.est_width(name, size, "700") + size * 0.5,
                   baseline, value, size, anchor="start")
        elif kind == "right":
            size = c.fit_size(str(payload), inner * 0.6, span * 0.60, "700")
            c.text(x + w - pad, baseline, str(payload), size,
                   weight="700", anchor="end")
        elif kind == "nutrient":
            name, amount, dv = payload
            dv_w = c.est_width(dv, span * 0.62, "700")
            # name + gap + amount must clear the right-aligned daily value
            budget = inner - dv_w - span * 0.35
            size = c.fit_size(f"{name} {amount}", budget, span * 0.62, "700")
            c.text(x + pad, baseline, name, size, weight="700", anchor="start")
            c.text(x + pad + c.est_width(name, size, "700") + size * 0.45,
                   baseline, amount, size, anchor="start")
            c.text(x + w - pad, baseline, dv, size, weight="700", anchor="end")
        elif kind == "small":
            size = c.fit_size(str(payload), inner, span * 0.60)
            c.text(x + pad, baseline, str(payload), size, anchor="start")
        cur += span


def distributor_block(c: Canvas, x: float, y_bottom: float, height: float,
                      lines: list[str]) -> None:
    """The rotated block that sits outboard of the nutrition panel."""
    size = height * 0.035
    with c.group(f"translate({x:.1f} {y_bottom:.1f}) rotate(-90)"):
        for i, line in enumerate(lines):
            c.add(f'<text x="0" y="{i * size * 1.30:.1f}" font-family="Inter" '
                  f'font-size="{size:.1f}" font-weight="{"700" if i == 0 else "400"}" '
                  f'text-anchor="start" fill="#000000">{c.esc(line)}</text>')


def descriptor(c: Canvas, cx: float, y: float, title: str, volume: str,
               size: float) -> None:
    """Centred product descriptor, widely letterspaced."""
    c.text(cx, y, title, size, weight="800", ls=size * 0.36)
    c.text(cx, y + size * 1.10, volume, size * 0.70, weight="500", ls=size * 0.14)


def volume_label(c: Canvas) -> str:
    """Volume string derived from the profile's capacity."""
    ml = c.capacity_ml or 500
    fl_oz = ml / 29.5735
    return f"{fl_oz:.1f} FL Oz / {ml} mL" if ml < 1000 else f"{fl_oz:.1f} FL Oz / {ml/1000:g} L"


def cert_row(c: Canvas, x: float, y: float, gap: float, size: float,
             labels: tuple[str, ...] = ("BPA FREE", "RECYCLABLE", "MADE WITH LOVE")
             ) -> None:
    """Placeholder certification marks.

    These are drawn, not the real assets. When the component library has been
    extracted, place ``engine.components.LIBRARY`` images instead — several of
    the real marks are trademarks and must not be approximated.
    """
    r = size * 0.5
    for i, label in enumerate(labels):
        cx = x + i * gap
        if i == 0:
            c.circle(cx, y, r, c.MED)
            c.heart_outline(cx, y + r * 0.05, r * 0.8, c.LIGHT)
        elif i == 1:
            for k in range(3):
                with c.group(f"rotate({k*120} {cx:.1f} {y:.1f})"):
                    c.path(f"M {cx-0.62*r:.1f} {y+0.36*r:.1f} "
                           f"L {cx-0.14*r:.1f} {y-0.47*r:.1f}", c.HEAVY)
                    c.filled(f"M {cx-0.14*r:.1f} {y-0.62*r:.1f} "
                             f"L {cx+0.12*r:.1f} {y-0.30*r:.1f} "
                             f"L {cx-0.38*r:.1f} {y-0.30*r:.1f} Z")
        else:
            c.circle(cx, y, r, c.MED)
            c.star(cx, y, r * 0.8)
        c.text(cx, y + r * 1.75, label, r * 0.46, weight="800", ls=r * 0.05)
