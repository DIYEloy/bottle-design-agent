# Initial architecture

## Workflow

1. Collect a theme and one of the five bottle profiles.
2. Accept optional user-provided reference images and approved brand/content assets.
3. Analyze references and create a compact design brief.
4. Generate a vector-first SVG composition.
5. Render a low-resolution preview for approval.
6. After approval, render the exact profile dimensions and validate the files.
7. Export PNG, SVG, PDF, and PSD where the layered export path is supported and verified.

## Output policy

- Black-and-white artwork only.
- Target resolution: 1200 DPI for raster exports.
- SVG is the editable vector master wherever practical.
- Do not upscale low-resolution user assets silently. Flag insufficient effective resolution.
- Preserve user-provided logos, wording, and reference assets; request clarification rather than replacing them.
- Do not claim a PSD is layered/editable until the export implementation and compatibility have been tested.

## Large-file strategy

The largest current canvas is 12,000 × 6,000 px (72 megapixels). Keep inter-agent messages lightweight: pass SVG, JSON layout instructions, asset IDs, and file paths rather than base64-encoded full-resolution images. Use temporary files or object storage for large intermediate renders. Create production-size outputs only after preview approval.

## Open production questions

Printer-specific bleed, seam overlap, safe area, substrate behavior, and accepted PSD flavor are not yet specified. Current profile safe margins are placeholders and must be calibrated against the actual bottle and transfer workflow.
