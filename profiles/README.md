# Bottle profiles

Each JSON file is the single source of truth for one supported bottle template.

- Pixel dimensions are width × height, as supplied by the user.
- Resolution target is 1200 DPI.
- Physical dimensions are derived from pixels ÷ DPI × 25.4.
- Artwork is black and white. Grayscale may be used internally where approved, but final color policy must be enforced at export.
- The 3 mm safe margin is an initial configurable default, not a verified printer specification.
- Confirm wrap overlap, bleed, seam position, and printer-specific tolerances before production.
