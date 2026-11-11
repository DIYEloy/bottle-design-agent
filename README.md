# Bottle Design Agent

An AI-assisted, vector-first workflow for creating black-and-white sublimation artwork for custom bottles.

## Current project status

This is the first scaffold. It defines the five supplied bottle profiles, the modular agent responsibilities, and a deterministic profile-validation foundation. Artwork composition, rendering, ChatGPT-facing integration, and export adapters are future milestones.

## Supported bottle templates

All pixel dimensions are **width × height** at a target of **1200 DPI**.

| Profile | Canvas (px) | Physical size (mm) |
|---|---:|---:|
| FAT 250 ml | 9000 × 2400 | 190.5 × 50.8 |
| FAT 500 ml | 9000 × 6000 | 190.5 × 127 |
| FAT 1 L | 12000 × 6000 | 254 × 127 |
| LONG 500 ml | 9000 × 4560 | 190.5 × 96.52 |
| LONG 1 L | 12000 × 6000 | 254 × 127 |

Profile definitions live in `profiles/`. Physical dimensions are calculated from pixels ÷ DPI × 25.4.

## Design and production rules

- Artwork is black and white.
- User-provided logos, photographs, wording, and approved reference assets take priority. Do not silently replace them with generic alternatives.
- Use SVG as the vector master wherever practical.
- Generate a lightweight preview first. Produce full-resolution output only after the user approves the design.
- Check the effective resolution of raster uploads; never silently imply that an undersized image is print-ready.
- Export targets: PDF, PNG, SVG, and PSD. PSD support must be verified before claiming that its layers are editable.
- Printer-specific bleed, seam overlap, and safe areas must be confirmed before production. The current 3 mm safe margin is only a placeholder.

## Architecture

See [docs/architecture.md](docs/architecture.md) and [agents/README.md](agents/README.md).

LLM agents handle conversation, reference analysis, design planning, and review. Deterministic code handles geometry, rendering, color enforcement, file export, and technical validation. Large raster files should remain in file storage; agents should exchange compact briefs, asset references, and vector fragments.

## Development

Python 3.11 or newer is required.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

Load a profile from Python:

```python
from engine.profiles import load_profile

profile = load_profile("fat_500ml")
print(profile["width_px"], profile["height_px"], profile["dpi"])
```

## Repository layout

- `agents/` — agent roles and prompts
- `engine/` — deterministic profile, layout, render, and validation code
- `profiles/` — bottle templates
- `assets/` — approved user-supplied assets (not committed unless authorized)
- `docs/` — architecture and production notes
- `tests/` — automated tests
- `output/` — local generated files; production artwork is ignored by Git

## Roadmap

1. Profile-aware SVG canvas and preview generator.
2. Asset intake and image-resolution checks.
3. Layout primitives and reusable bottle elements.
4. Black-and-white and safe-area validation.
5. PNG/PDF/SVG export pipeline.
6. Layered PSD export and compatibility tests.
7. ChatGPT interface and orchestrated specialist agents.


## Continue work in another chat

See [docs/CHAT_HANDOFF.md](docs/CHAT_HANDOFF.md) for the complete project state, fixed requirements, current limitations, rev0.1 definition of done, engineering rules, and a ready-to-use continuation prompt. Continue on `feat/initial-agent-scaffold`; do not merge without the user's instruction.
