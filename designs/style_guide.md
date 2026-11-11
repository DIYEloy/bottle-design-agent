# House style guide

Derived by measuring supplied production files, not invented. Every number
here traces to a specific template. Machine-readable constants live alongside
this file in `style.json`; this document explains *why* each value is what it
is.

Update both together when new reference artwork arrives.

## Reference files measured

| Job | Profile | Technique | Source |
|---|---|---|---|
| BOCAS GRILL | FAT 500 ml, 9000x6000 | Hand-drawn line art | flattened PSD |
| THE BAR·ZAAR | FAT 250 ml, 9000x2400 | Photographic halftone | layered PSD |
| TACO RICO | LONG 500 ml | Line art, 3-panel | presentation mockup |

## The core finding: furniture vs artwork

There is no single house style. Measured side by side, two production jobs
differ by 3x in ink coverage and 15x in mid-tone content:

| | BOCAS (line art) | BAR·ZAAR (halftone) |
|---|---|---|
| Pure black | 8.03% | 24.61% |
| Pure white | 91.22% | 64.04% |
| Mid-tones | 0.75% | 11.36% |

What *is* constant is the **furniture**: the regulatory and brand elements
that appear on every bottle in the same relative positions. Treat the two
layers separately.

- **Furniture layer** — nutrition panel, certification marks, distributor
  block, product descriptor, social row. Standardised; belongs in code.
- **Artwork layer** — the client's creative. Varies freely in technique.

Design generators should hold the furniture fixed and vary only the artwork.

## Canvas and safe area

All profiles are 1200 DPI. Width is the wrap circumference; height is the
label height.

Both FAT production templates keep **all content within ~7800 px of the
9000 px canvas**, leaving roughly 600 px per side:

| Template | Content bounds | Left margin | Right margin |
|---|---|---|---|
| FAT 500 | 920–8156 (7236 px) | 920 | 844 |
| FAT 250 | 681–8318 (7637 px) | 681 | 682 |

7800 px at 1200 DPI is 165.1 mm — exactly the artboard size of the supplied
Illustrator template, against the PSD canvas of 190.5 mm. The 25.4 mm
difference is **12.7 mm (0.5 in) of seam overlap per side**.

> **Not printer-confirmed.** This is derived from two templates of one bottle
> shape. The value is carried into LONG and 1 L profiles as an assumption and
> flagged `safe_area_source: assumed-from-FAT-templates` there. Confirm against
> a physical bottle before production.

## Colour

One ink: black. The TACO RICO spec sheet states `IMPRESIÓN: 1 tinta (negro)
sobre botella transparente`.

**On a clear bottle there is no white ink.** White in the artwork is not
printed — it is the transparent bottle and the water behind it. This means:

- Never rely on white as a figure colour; it is a hole, not a mark.
- Knockout text inside a black shape works. White text on nothing does not.
- Ink coverage is a cost and drying consideration, not just an aesthetic one.

Permitted greys are **rasterisation anti-aliasing only** — expect under 1% of
pixels in line-art work. Tonal imagery is achieved by halftone screening, not
by grey ink (see below).

## Halftone technique

The BAR·ZAAR job carries photographic imagery while remaining strictly
black-and-white, by screening the photo into a dot pattern. Measured at
roughly 11% mid-tone when sampled below the dot pitch; at full resolution the
dots are discrete black marks.

Use `engine.halftone` to reproduce this. It converts any photograph to a 1-bit
screen at a configurable dot pitch. This is the sanctioned route for imagery
that cannot be drawn as line art.

## Layout grammar

Observed across jobs, in rough order of reliability:

1. **Zone-based, not centred.** Content is distributed into distinct regions
   rather than composed around a single axis.
2. **Nutrition panel sits in a bottom or side corner**, boxed, with the
   distributor block rotated 90° immediately outboard of it.
3. **Certification marks cluster together**, away from the nutrition panel.
4. **Product descriptor** (`PURIFIED WATER`, volume) is centred and widely
   letterspaced.
5. **Panel division.** The TACO RICO job divides the wrap into three discrete
   panels — `LADO 1`, `FRENTE`, `LADO 2` — rather than one continuous
   composition. Front carries the wordmark; one side carries the QR and
   short claims; the other carries logo, nutrition and certification. Treat
   panel count as a job parameter.

## Typography

Measured from the supplied files; substitutes noted where the original font is
unavailable.

- **Display / wordmark** — heavy grotesque, tight tracking. `Inter` at weight
  900 is the working substitute.
- **Furniture labels** — same family, weights 600–800, wide tracking
  (40–60/1000 em) for small caps lines.
- **Script accents** — chancery italic for phrases like *Join us*,
  *Alkaline Purified Water*. `TeX Gyre Chorus` is the working substitute.
- **Nutrition panel** — follows the FDA layout: bold rules of varying weight
  separating sections, name left, amount inline, `% Daily Value` right.

## Stroke weights

Expressed against a 9000 px wide canvas; scale proportionally for other
canvases.

| Name | px at 9000 wide | Use |
|---|---|---|
| `HEAVY` | 26 | Medallion rings, primary rules |
| `MED` | 16 | General linework, motif outlines |
| `LIGHT` | 11 | Secondary rules, inner detail |
| `HAIR` | 7 | Nutrition panel rules, fine detail |

## Nutrition panel data

The panel is standard FDA layout with water values, but **serving count is
derived from bottle capacity, not copied**:

| Capacity | Servings per container |
|---|---|
| 250 ml | about 1 |
| 500 ml | about 2 |

A hemp/CBD variant panel exists in the supplied 250 ml master with additional
Delta-9 THC disclosure text. Treat panel variant as a job parameter.

## Component inventory

24 reusable assets were extracted from the supplied 250 ml layered master.
They are customer assets and are **not committed** (see `assets/README.md`).

- **Certification**: Made in Miami, No Label = Easier Recycling, BPA Free,
  Made in USA
- **Social**, in three shape families named in the source file:
  `redondo` (circle), `cuadrado` (rounded square), `sencillo` (bare glyph) —
  Instagram, Facebook, Twitter, WhatsApp, YouTube, Yelp, TripAdvisor, email,
  web, phone, location

Several are registered trademarks. Place the supplied assets; do not redraw
them.

## Deliverable formats

Beyond the print files, jobs are presented to clients as a **mockup sheet**:
bottle renders alongside flat panels, with a specification bar stating bottle
type, cap colour, print process and artwork description. See the TACO RICO
reference.
