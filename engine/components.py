"""Load and place the reusable furniture components.

Components are the brand and regulatory elements that repeat on every bottle:
certification marks and social icons. They are customer assets, so the images
live in ``assets/`` (gitignored) and only ``manifest.json`` is tracked.
Regenerate them with ``tools/extract_components.py``.

Components are placed by physical size in millimetres, not pixels, so the same
call produces correctly scaled output on any profile.
"""
from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_DIR = _ROOT / "assets" / "components"


class ComponentsUnavailable(RuntimeError):
    """Raised when the asset library has not been extracted yet."""


@dataclass(frozen=True)
class Component:
    slug: str
    layer_name: str
    role: str
    family: str | None
    path: Path
    width_px: int
    height_px: int
    width_mm: float
    height_mm: float

    @property
    def aspect(self) -> float:
        return self.width_px / self.height_px if self.height_px else 1.0


class ComponentLibrary:
    """Lazy index over the extracted component assets."""

    def __init__(self, directory: Path | str | None = None):
        self.directory = Path(directory) if directory else _DEFAULT_DIR
        self._index: dict[str, Component] | None = None

    # -- loading -------------------------------------------------------
    @property
    def manifest_path(self) -> Path:
        return self.directory / "manifest.json"

    def available(self) -> bool:
        return self.manifest_path.exists()

    def _load(self) -> dict[str, Component]:
        if self._index is not None:
            return self._index
        if not self.available():
            raise ComponentsUnavailable(
                f"No component manifest at {self.manifest_path}. "
                "Run: python tools/extract_components.py <master.psd>"
            )
        data = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        index: dict[str, Component] = {}
        for entry in data.get("components", []):
            index[entry["slug"]] = Component(
                slug=entry["slug"],
                layer_name=entry["layer_name"],
                role=entry["role"],
                family=entry.get("family"),
                path=self.directory / entry["file"],
                width_px=entry["width_px"],
                height_px=entry["height_px"],
                width_mm=entry["width_mm"],
                height_mm=entry["height_mm"],
            )
        self._index = index
        return index

    # -- queries -------------------------------------------------------
    def __contains__(self, slug: str) -> bool:
        try:
            return slug in self._load()
        except ComponentsUnavailable:
            return False

    def get(self, slug: str) -> Component:
        index = self._load()
        if slug not in index:
            raise KeyError(
                f"unknown component {slug!r}; available: {sorted(index)}"
            )
        return index[slug]

    def by_role(self, role: str) -> list[Component]:
        return [c for c in self._load().values() if c.role == role]

    def by_family(self, family: str) -> list[Component]:
        return [c for c in self._load().values() if c.family == family]

    def slugs(self) -> list[str]:
        return sorted(self._load())

    def missing(self, slugs: list[str]) -> list[str]:
        """Which of these slugs are not present. Use for job validation."""
        try:
            index = self._load()
        except ComponentsUnavailable:
            return list(slugs)
        return [s for s in slugs if s not in index]

    # -- placement -----------------------------------------------------
    def svg_image(
        self,
        slug: str,
        *,
        x_px: float,
        y_px: float,
        height_mm: float,
        dpi: int,
        anchor: str = "top-left",
    ) -> str:
        """Return an SVG <image> element placing this component.

        Scaled to ``height_mm`` at the profile's ``dpi``, preserving aspect.
        ``anchor`` is one of ``top-left``, ``center``, ``bottom-left``.
        """
        comp = self.get(slug)
        if not comp.path.exists():
            raise ComponentsUnavailable(
                f"manifest lists {slug!r} but {comp.path} is missing; re-extract"
            )
        h = height_mm / 25.4 * dpi
        w = h * comp.aspect
        if anchor == "center":
            x_px, y_px = x_px - w / 2.0, y_px - h / 2.0
        elif anchor == "bottom-left":
            y_px = y_px - h
        elif anchor != "top-left":
            raise ValueError(f"unknown anchor: {anchor!r}")
        data = base64.b64encode(comp.path.read_bytes()).decode("ascii")
        return (
            f'<image x="{x_px:.1f}" y="{y_px:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'xlink:href="data:image/png;base64,{data}" '
            f'href="data:image/png;base64,{data}"/>'
        )


LIBRARY = ComponentLibrary()


def servings_for_capacity(capacity_ml: int) -> str:
    """Nutrition panel serving count, derived rather than copied.

    The supplied masters show 'about 1' at 250 ml and 'about 2' at 500 ml,
    against a fixed 8 fl oz (237 ml) serving size.
    """
    if capacity_ml <= 0:
        raise ValueError("capacity_ml must be positive")
    servings = capacity_ml / 237.0
    return f"about {max(1, round(servings))}"
