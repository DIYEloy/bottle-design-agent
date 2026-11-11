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

## Real artwork vs mock output

`agents/mock_backend.py` produces a technical placeholder (a border and the
theme as a title) so the pipeline runs without API keys. It is not a design
generator.

Finished, printable artwork lives in `designs/`. See
[designs/README.md](designs/README.md).

```bash
python -m designs.baby_shower_fat500 --outdir output --raster
```

## Model tiering (cost)

Specialists are routed by tier, so only the steps that need reasoning get an
expensive model. See `agents/tiered.py`.

| Tier | Agents | Calls per job |
|---|---|---|
| `BRAIN` | theme_planner, layout | 2 |
| `WORKER` | image_analysis, asset_placement, quality_review | 3 |
| `LOCAL` | rendering, halftoning, export, measurement | 0 |

Credentials come from the environment only. With none set, the offline mock
backend runs and the pipeline stays usable.

```bash
export BOTTLE_PROVIDER=anthropic       # or openai
export BOTTLE_BRAIN_MODEL=<model-id>
export BOTTLE_WORKER_MODEL=<small-model-id>
export ANTHROPIC_API_KEY=...
```

## HTTP API

```bash
pip install -e ".[api]"
uvicorn api.app:app --reload
```

`POST /jobs` submits a job and returns an id; `GET /jobs/{id}` polls it;
`GET /jobs/{id}/files/{name}` downloads artwork. Preview-first is the default:
production export requires `auto_export: true` or a separate approved run.
Not authenticated — see the deployment notes in `api/app.py` before exposing it.

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
- `designs/` — real artwork generators, plus `style_guide.md` and `style.json`
- `api/` — HTTP API for automated generation
- `tools/` — asset extraction utilities
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
8. Proportional layout so one design reflows across every profile.
9. Shared brand components (nutrition panel, certification icons, social row).


## Continue work in another chat

See [docs/CHAT_HANDOFF.md](docs/CHAT_HANDOFF.md) for the complete project state, fixed requirements, current limitations, rev0.1 definition of done, engineering rules, and a ready-to-use continuation prompt. Continue on `feat/initial-agent-scaffold`; do not merge without the user's instruction.


## Run rev0.1 locally (offline mock mode)

Install Python 3.11+, then:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
bottle-agent profiles
bottle-agent validate examples/sample_job.json
bottle-agent preview examples/sample_job.json --output output/preview.png
```

The preview command runs the deterministic mock agents and writes a small PNG preview plus a JSON report. It does not call an AI model or inspect image pixels.

After reviewing a preview, production-size export is an explicit operation:

```bash
bottle-agent export examples/sample_job.json --output-dir output --approve
```

This writes the exact profile-size PNG, physical-size vector SVG, and PDF. A flattened PSD is generated only if ImageMagick is installed; the report clearly marks it as flattened. Install ImageMagick separately if a flattened PSD is needed. Layered PSD authoring is not claimed in rev0.1.

### Current rev0.1 boundaries

- The offline mock backend makes the workflow runnable without API keys; it is not a substitute for a vision-capable AI provider.
- The current mock composition is a technical starter layout, not a polished design generator.
- Raster asset placement and advanced typography/layout are future refinements.
- Printer-specific seam, bleed, and safe-area settings must be calibrated against a physical bottle and transfer process.
- The 1200 DPI raster canvas can be very large. Ensure adequate RAM and disk space before production export.
