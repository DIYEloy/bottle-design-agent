# Designs

Real, non-mock artwork generators. Each module here produces finished
black-and-white vector artwork for a bottle profile, as opposed to the
deterministic placeholder layout in `agents/mock_backend.py`.

## Why these exist

The `agents/` package defines a provider-neutral `AgentBackend` protocol, but
no model provider is wired up, so the only implementation is `MockBackend` —
which emits a bordered rectangle and the job's theme as a title. That is enough
to exercise the pipeline, and not enough to print.

These modules close that gap from the other side: the *design decisions* are
made up front and expressed directly as vector primitives, while the canvas
spec, dimensions, and DPI still come from `profiles/`.

## Running

```bash
python -m designs.baby_shower --profile fat_500ml --outdir output --raster
python -m designs.baby_shower --all --outdir output          # every profile
```

- without `--raster`: writes the SVG master only (fast)
- with `--raster`: also writes the `1200` DPI PNG at exact profile pixel
  dimensions and a PDF at true physical size

## Conventions

- Canvas size and DPI are read from `profiles/<id>.json`. Never hardcode them.
- Output is pure black on white. The only grey permitted is edge
  anti-aliasing from rasterisation (expect well under 1% of pixels).
- SVG is the editable master; PNG and PDF are derived.
- Stroke weights are expressed against the full-resolution canvas:
  `HEAVY=26`, `MED=16`, `LIGHT=11`, `HAIR=7` at 9000 px wide.

## Responsive layout

One composition serves all five profiles, which differ in aspect ratio by
2.5x. Pure scaling cannot do this: a 7800x6000 layout squeezed into 7800x2400
overflows by a factor of two and a half. Instead the design selects an
*arrangement* by aspect band, then places everything in normalised
coordinates inside the printable sector.

| Band | Aspect (h/printable w) | Profiles | Arrangement |
|---|---|---|---|
| `tall` | >= 0.65 | fat_500ml | Three bands: hero, medallions, footer |
| `medium` | 0.40 - 0.65 | fat_1l, long_1l, long_500ml | Two bands, no side column |
| `short` | < 0.40 | fat_250ml | Single horizontal strip |

Two sizing systems, deliberately. Decorative sizes (`c.s(...)`) scale with the
canvas; furniture sizes (`c.mm(...)`) are absolute millimetres, because a
nutrition panel must stay legible at a fixed physical size. Legibility does
not scale.

## Known limitations

- **Text is rendered as live text, not outlines.** The SVG master depends on
  `Inter` and `TeX Gyre Chorus` being installed to render identically
  elsewhere. The exported PNG and PDF embed the glyphs and are unaffected.
- **Text metrics are estimated, not measured.** `Canvas.est_width` approximates
  rendered width from character count to avoid a font-metrics dependency. It
  is tuned to prevent overflow rather than to be exact, so it errs toward
  shrinking text slightly more than necessary.
- Illustrations are constructed from geometric primitives. They are clean and
  consistent, but they are not hand-drawn character illustration.
- `cert_row` draws placeholder marks. Once the component library is extracted,
  place the real assets through `engine.components` instead -- several are
  trademarks and must not be approximated.

## Reusable brand components

Nutrition panel, certification icons, social row, and the product descriptor
are currently inlined in each design. These are the same on every bottle and
should become parameterised components. Extracting them is tracked as the next
step; see the repository README.
