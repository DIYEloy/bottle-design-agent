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
python -m designs.baby_shower_fat500 --outdir output --raster
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

## Known limitations

- **Coordinates are absolute, not proportional.** `baby_shower_fat500` is laid
  out for a 9000x6000 canvas. Pointing `PROFILE_ID` at a differently shaped
  profile will reflow the canvas but *not* rescale the composition. Making the
  layout proportional is the single highest-value improvement here.
- **Shared primitives are not yet extracted.** The drawing helpers and motif
  functions are duplicated per design module. They belong in a shared
  `designs/primitives.py` once a second design exists to validate the
  interface.
- **Text is rendered as live text, not outlines.** The SVG master depends on
  `Inter` and `TeX Gyre Chorus` being installed to render identically
  elsewhere. The exported PNG and PDF embed the glyphs and are unaffected.
- Illustrations are constructed from geometric primitives. They are clean and
  consistent, but they are not hand-drawn character illustration.

## Reusable brand components

Nutrition panel, certification icons, social row, and the product descriptor
are currently inlined in each design. These are the same on every bottle and
should become parameterised components. Extracting them is tracked as the next
step; see the repository README.
