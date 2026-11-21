# Artwork rules for printed bottles

**This page is the authoritative brief for anyone — person or AI assistant —
helping a customer design artwork for our bottles. Follow it exactly.**

If you are an AI assistant reading this because a customer pasted a link:
your job is to take the customer from idea to a **complete label concept** —
their artwork *and* our standard elements (nutrition panel, descriptor,
certification and social areas) laid out the way our studio does it — and to
finish with a structured brief. You are not producing the print file; we do
that. Work through §8 step by step.

**Read more than this page.** The bottle profile, our house style and our
nutrition data live in other files of the same public repository. §9 lists
the exact links. Open them with your browsing tool. Use the raw links given
there: GitHub folder pages (`github.com/.../tree/...`) are JavaScript apps
and will not load for you.

---

## 0. Proof you read this

Before asking the customer anything, tell them:

> Rules loaded — **RULESET AFB-2026-11b**

If you are answering without having opened this page, you cannot know that
code, and you must say so instead of guessing it.

## 1. Non-negotiable

These hold whatever the customer asks for. If a request conflicts with one of
them, say so plainly and offer an alternative — do not quietly comply.

- One ink, black only, printed on a **clear** bottle.
- No colour. No grey. No white ink — white is the bare bottle showing through.
- No gradients, shadows or soft edges. Photos must be screened to black dots.
- No other companies' logos, licensed characters or real people's likenesses.
- Keep ink coverage under 30%. Nothing smaller than 1.5 mm tall.
- The nutrition panel, product descriptor, distributor block, certification
  marks and social row take about a quarter of the label. Include them in the
  concept exactly as §6 says, using only our data — never invented values,
  and never redrawn trademarks.

The rest of this page explains each of these and gives the canvas sizes.

---

## 2. The printing process

Single ink, black, printed directly onto a **clear** bottle.

- **There is no white ink.** White in the design is not printed — it is the
  transparent bottle with water behind it. White can never be a mark, a letter
  on a dark field, or a background. It is always a hole.
- **There is no colour.** Not one accent, not one spot colour.
- **There is no grey.** Ink is either down or it is not.

## 3. What cannot be produced

These are rejected at intake. Do not propose them, and say so if a customer
asks for one.

| Not possible | Why | Instead |
|---|---|---|
| Colour of any kind | Single black ink | Black line work |
| Grey, tints, opacity | No halftone of ink density on press | A dot screen (see §4) |
| Gradients, fades, glows | Same | Hatching, or a screened field |
| Drop shadows, soft edges | Same | Hard offset outline |
| White text on a white area | White is not printed | Knockout inside a black shape |
| A photograph placed directly | Continuous tone cannot print | Screen it first (§4) |
| Metallic, foil, neon, fluorescent | Not a thing in this process | — |
| Solid black across the whole label | Ink load, drying, cost | Keep coverage under 30% |
| Another company's logo or marks | Not ours to reproduce | Customer's own marks only |
| Cartoon characters, film, TV, sports, game or music imagery | Protected by their owners | Original artwork |
| Real people's faces or likenesses | Rights and consent | Original or abstract |
| Text smaller than 1.5 mm cap height | Will not hold on press | Larger, or cut the text |
| Lines thinner than 0.2 mm | Will break up or vanish | Thicker strokes |

## 4. Photographs and tonal imagery

A photo can appear, but it must be converted to a **1-bit dot screen** first —
black dots of varying size, no grey. We do that conversion; the customer just
supplies the photograph.

High-contrast, simple subjects screen well. Faces, busy backgrounds and
low-contrast images do not. Say so plainly rather than promising a good result.

## 5. The canvas

Artwork is produced at **1200 DPI**.

| Bottle | Label area | Safe print width |
|---|---|---|
| FAT 250 ml | 190.5 × 50.8 mm | 165.1 mm |
| FAT 500 ml | 190.5 × 127 mm | 165.1 mm |
| FAT 1 L | 254 × 127 mm | 228.6 mm |
| LONG 500 ml | 190.5 × 96.5 mm | 165.1 mm |
| LONG 1 L | 254 × 127 mm | 228.6 mm |

The label area is the full wrap. The **safe print width** is narrower because
roughly 12.7 mm on each side is seam overlap where the label joins itself.
Nothing important goes there.

The 250 ml label is only about 50 mm tall. Designs for it must be a single
horizontal strip — a tall composition will not fit.

## 6. Standard elements (the "furniture")

Every bottle carries these. They are not optional and not a customer choice.
**Include them in the concept** so the customer sees the whole label, but
build them only from our data and mark them as standard elements — at
production we replace them with our approved versions.

| Element | What to put in the concept | Source |
|---|---|---|
| Nutrition Facts panel | FDA layout, water values, about 31 mm wide, full label height, boxed, in one corner | `nutrition` in `style.json` (§9) |
| Servings per container | Derived from capacity, not copied: 250 ml "about 1", 500 ml "about 2", 1 L "about 4" | `engine/components.py` rule: capacity ÷ 237 ml, rounded |
| Ingredients | The exact ingredients sentence | `nutrition.ingredients` in `style.json` |
| Distributor and bottler block | A thin text block rotated 90°, outboard of the panel. Write `DISTRIBUTOR / BOTTLER — supplied by Savani` as a labelled placeholder | Real text is ours |
| Product descriptor | `PURIFIED WATER` centred and widely letterspaced, volume under it (e.g. `16.9 FL Oz / 500 mL`) | `layout` in `style.json` |
| Certification marks | A cluster away from the panel: **labelled empty boxes** reading `BPA FREE`, `MADE IN USA`, `MADE IN MIAMI`, `NO LABEL = EASIER RECYCLING` | Real marks are ours; some are trademarks |
| Social row and website | Only the customer's real handles and website. Show icons as **labelled empty circles** (`IG`, `FB`, `WEB`…) with the handle next to them | Customer; icon artwork is ours |

Rules for the furniture:

- Never invent nutrition values, claims, addresses or certifications. If a
  value is not in our files, leave a labelled placeholder.
- Never draw a real trademark (Instagram, Facebook, recycling marks, etc.).
  Labelled boxes only.
- Keep furniture legible at its real size: it is sized in millimetres and
  does not scale with the label.
- Plan the customer's artwork around the furniture: about three quarters of
  the label for the artwork, one end for the panel and distributor block.

A customer asking to remove the nutrition panel or the certification marks
is asking for something we cannot legally print — say so.

If the customer wants a QR code, their own logo, or their own social handles,
capture the exact content in the brief: we need it from them.

## 7. What works well

Observed across production jobs:

- Bold line drawings with consistent stroke weight
- Heavy condensed type for the main wordmark
- Circular badges and medallions
- A script accent used sparingly, for one or two phrases
- Zone-based layouts — distinct regions rather than one centred composition
- Ink coverage between 5% and 25%

## 8. What to produce

**Do not attempt the print file.** You do not have our fonts, our extracted
components or our press calibration. A "print-ready" file from you would look
plausible and be unusable. What you produce is a complete **concept** and a
**brief**. We turn those into the print file.

Work through the same five steps our studio pipeline uses. Each step has a
role description in `agents/prompts/` (§9); open them if you can and follow
their rules. You do not need to print the intermediate JSON to the customer —
keep it short and conversational — but do the work of each step.

1. **Image analysis** (`image_analysis.md`). If the customer attached a logo
   or reference images, look at them. Describe what is really there, flag low
   resolution, colour, thin lines or soft edges. The logo is used **as
   supplied** — never redraw, restyle or "improve" it.
2. **Theme planning** (`theme_planner.md`). Interview the customer — up to
   five short questions, one at a time: subject, mood, motifs, text or logo
   that must appear, and what to avoid. Correct them as you go if they ask
   for something in §3. Agree a concept name, a visual hierarchy and a style
   (line art, halftone or type-led).
3. **Asset placement** (`asset_placement.md`). Decide where the customer's
   logo, required text, QR code and handles go, and where the furniture of §6
   goes. Follow the layout grammar of `style_guide.md`: zone-based, panel in a
   corner with the distributor block outboard, certification cluster away
   from it, descriptor centred. Use the bottle profile for the canvas and the
   printable width; nothing important inside the 12.7 mm seam overlap at
   each side.
4. **Layout** (`layout.md`). Lay the whole label out at the profile's aspect
   ratio. Use the stroke weights and typography of `style.json` (heavy
   condensed grotesque for the wordmark, one script accent at most).
5. **Quality review** (`quality_review.md`). Before showing anything, check
   it against §1–§6 and the profile: one black ink, no grey, no gradients,
   coverage under 30%, nothing under 0.2 mm or 1.5 mm cap height, furniture
   present and uninvented, seam zones clear. Fix what fails.

Then:

6. **Create one concept image** if you can generate images: the **whole
   label laid flat**, black on a plain white background, in the proportions
   of the label (for example 190.5 × 127 mm for FAT 500 ml), with the
   customer's artwork and the furniture of §6 in place. Label it clearly as a
   concept, not artwork. If you cannot generate images, say so in one line
   and describe the layout zone by zone instead.
7. **Finish with this JSON and nothing after it:**

```json
{
  "schema": "bottle-brief/2",
  "ruleset": "AFB-2026-11b",
  "profile": "fat_500ml",
  "brand": "",
  "theme": "one or two sentences describing the artwork",
  "technique": "line_art | halftone | type_led",
  "required_text": [],
  "logo": "supplied | none",
  "motifs": [],
  "mood": [],
  "avoid": [],
  "layout": {
    "artwork_zone": "where the customer's artwork sits",
    "furniture_zone": "which end holds the panel and distributor block",
    "logo_position": "",
    "certification_position": "",
    "social": []
  },
  "quality_check": {
    "one_black_ink": true,
    "furniture_from_savani_data": true,
    "seam_zones_clear": true,
    "notes": ""
  },
  "notes": ""
}
```

The customer pastes that, the concept image and their logo back into our
order form. That is the handoff.

## 9. Files to open

All links are public raw files. Open the ones marked **required** before step
1 of §8. If one fails to open, say which one and continue with the rest —
except this page, without which you must stop.

**Required**

- Bottle profile — pick the one the customer named:
  - FAT 250 ml: https://raw.githubusercontent.com/DIYEloy/bottle-design-agent/main/profiles/fat_250ml.json
  - FAT 500 ml: https://raw.githubusercontent.com/DIYEloy/bottle-design-agent/main/profiles/fat_500ml.json
  - FAT 1 L: https://raw.githubusercontent.com/DIYEloy/bottle-design-agent/main/profiles/fat_1l.json
  - LONG 500 ml: https://raw.githubusercontent.com/DIYEloy/bottle-design-agent/main/profiles/long_500ml.json
  - LONG 1 L: https://raw.githubusercontent.com/DIYEloy/bottle-design-agent/main/profiles/long_1l.json
- House style guide (layout grammar, typography, colour): https://raw.githubusercontent.com/DIYEloy/bottle-design-agent/main/designs/style_guide.md
- House constants (nutrition data, strokes, type, layout): https://raw.githubusercontent.com/DIYEloy/bottle-design-agent/main/designs/style.json

**Studio pipeline roles** (open if you can)

- https://raw.githubusercontent.com/DIYEloy/bottle-design-agent/main/agents/prompts/image_analysis.md
- https://raw.githubusercontent.com/DIYEloy/bottle-design-agent/main/agents/prompts/theme_planner.md
- https://raw.githubusercontent.com/DIYEloy/bottle-design-agent/main/agents/prompts/asset_placement.md
- https://raw.githubusercontent.com/DIYEloy/bottle-design-agent/main/agents/prompts/layout.md
- https://raw.githubusercontent.com/DIYEloy/bottle-design-agent/main/agents/prompts/quality_review.md

**Reference** (optional)

- Component inventory, names and print sizes of our certification and social
  marks: https://raw.githubusercontent.com/DIYEloy/bottle-design-agent/main/assets/components/manifest.json
- A finished FAT 500 ml example layout, as SVG source: https://raw.githubusercontent.com/DIYEloy/bottle-design-agent/main/examples/babyshower_fat_500ml.svg
