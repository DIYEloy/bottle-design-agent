"""Extract reusable component assets from a layered PSD master.

The supplied FAT 250 ml master carries the brand and regulatory furniture as
named layers. This pulls each one out as a trimmed PNG plus a manifest entry
recording its real print size.

    python tools/extract_components.py TEMPLATE_FAT_250ML.psd --outdir assets/components

Images are written to ``assets/`` which is gitignored: these are customer
assets and the repository's engineering rules keep them out of version
control. Only ``manifest.json`` (metadata, no image data) is committed.

Note on layer visibility: layers nested inside a hidden group return a fully
transparent result from ``layer.composite()``. ``layer.numpy()`` returns the
real pixels regardless, so that is what this uses.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None

# Layer names observed in the supplied master, grouped by role.
CERTIFICATION = [
    "Made in Miami",
    "No Label Easier recycling",
    "BPA FREE",
    "made in usa",
]
SOCIAL = [
    "instagram cuadrado", "facebook cuadrado", "twitter cuadrado",
    "WEB DUADRADO", "yelp cuadrado", "tripadvisor", "email", "youtube",
    "telefono cuadrado", "loaction cuadrado", "WHATSAPP cuadrado",
    "INSTAGRAM SENCILLO", "FACEBOOK SENCILLO", "TWITTER SENCILLO",
    "WEB SENCILLO", "TELEFONO SENCILLO",
    "location redondo", "phone redondo", "web redondo", "email redondo",
]
WANTED = {n: "certification" for n in CERTIFICATION}
WANTED.update({n: "social" for n in SOCIAL})

# Shape family is encoded in the Spanish layer names.
FAMILY = {"redondo": "circle", "cuadrado": "rounded-square", "sencillo": "glyph"}


def _slug(name: str) -> str:
    return "".join(c if c.isalnum() else "_" for c in name.lower()).strip("_")


def _family_of(name: str) -> str | None:
    low = name.lower()
    for key, val in FAMILY.items():
        if key in low:
            return val
    return None


def extract(psd_path: Path, outdir: Path, dpi: int = 1200) -> list[dict]:
    from psd_tools import PSDImage

    psd = PSDImage.open(psd_path)
    outdir.mkdir(parents=True, exist_ok=True)
    entries: list[dict] = []
    seen: set[str] = set()

    def walk(layers) -> None:
        for layer in layers:
            if layer.is_group():
                walk(layer)
                continue
            if layer.name not in WANTED or layer.name in seen:
                continue
            if layer.bbox == (0, 0, 0, 0):
                continue
            try:
                arr = layer.numpy()
            except Exception:
                continue
            if arr is None or arr.ndim != 3 or arr.shape[2] < 4:
                continue
            rgb, alpha = arr[..., :3], arr[..., 3:4]
            over_white = rgb * alpha + 1.0 * (1.0 - alpha)
            img = Image.fromarray((np.clip(over_white, 0, 1) * 255).astype("uint8"))
            grey = img.convert("L")
            if grey.getbbox() is None or int((np.array(grey) < 250).sum()) < 50:
                continue
            seen.add(layer.name)
            slug = _slug(layer.name)
            path = outdir / f"{slug}.png"
            grey.save(path, optimize=True)
            x0, y0, x1, y1 = layer.bbox
            entries.append({
                "slug": slug,
                "layer_name": layer.name,
                "role": WANTED[layer.name],
                "family": _family_of(layer.name),
                "file": path.name,
                "width_px": x1 - x0,
                "height_px": y1 - y0,
                "width_mm": round((x1 - x0) / dpi * 25.4, 2),
                "height_mm": round((y1 - y0) / dpi * 25.4, 2),
                "source_dpi": dpi,
                "raster": True,
            })

    walk(psd)
    entries.sort(key=lambda e: (e["role"], e["slug"]))
    return entries


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("psd", type=Path)
    ap.add_argument("--outdir", type=Path, default=Path("assets/components"))
    ap.add_argument("--dpi", type=int, default=1200)
    ap.add_argument("--manifest", type=Path, default=None,
                    help="defaults to <outdir>/manifest.json")
    args = ap.parse_args()

    if not args.psd.exists():
        raise SystemExit(f"no such file: {args.psd}")
    entries = extract(args.psd, args.outdir, args.dpi)
    manifest = args.manifest or (args.outdir / "manifest.json")
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps(
        {"source": args.psd.name, "dpi": args.dpi, "components": entries},
        indent=2) + "\n", encoding="utf-8")
    print(f"extracted {len(entries)} components -> {args.outdir}")
    print(f"manifest -> {manifest}")
    for e in entries:
        print(f"  {e['slug']:28s} {e['width_mm']:5.1f} x {e['height_mm']:5.1f} mm  [{e['role']}]")


if __name__ == "__main__":
    main()
