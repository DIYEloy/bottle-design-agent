# Agent roles

Agents should exchange compact structured briefs, asset references, and SVG/vector fragments. Avoid passing full-resolution raster artwork between agents.

1. **Orchestrator** — collects the theme, profile, constraints, and approval checkpoints.
2. **Image analysis** — describes user-uploaded references and extracts usable visual guidance; never invents or substitutes approved brand assets.
3. **Theme planner** — proposes a visual direction and hierarchy.
4. **Asset placement** — places only user-approved logos, copy, icons, nutrition panels, and other supplied assets.
5. **Layout** — composes the vector artwork against the selected bottle profile.
6. **Quality review** — checks required content, margins, contrast, dimensions, and output readiness.
7. **Export** — coordinates deterministic rendering and file packaging.

The rendering and validation engine should remain deterministic code, not an LLM responsibility. Render small previews first; render full-resolution output only after approval.
