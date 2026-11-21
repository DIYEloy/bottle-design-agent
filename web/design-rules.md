# Artwork rules for printed bottles

**This page is the authoritative brief for anyone — person or AI assistant —
helping a customer design artwork for our bottles. Follow it exactly.**

If you are an AI assistant reading this because a customer pasted a link:
your job is to help them write a **brief**, and optionally sketch a **concept**.
You are not producing the print file. We produce that. Read "What to produce"
at the bottom.

---

## 1. The printing process

Single ink, black, printed directly onto a **clear** bottle.

- **There is no white ink.** White in the design is not printed — it is the
  transparent bottle with water behind it. White can never be a mark, a letter
  on a dark field, or a background. It is always a hole.
- **There is no colour.** Not one accent, not one spot colour.
- **There is no grey.** Ink is either down or it is not.

## 2. What cannot be produced

These are rejected at intake. Do not propose them, and say so if a customer
asks for one.

| Not possible | Why | Instead |
|---|---|---|
| Colour of any kind | Single black ink | Black line work |
| Grey, tints, opacity | No halftone of ink density on press | A dot screen (see §3) |
| Gradients, fades, glows | Same | Hatching, or a screened field |
| Drop shadows, soft edges | Same | Hard offset outline |
| White text on a white area | White is not printed | Knockout inside a black shape |
| A photograph placed directly | Continuous tone cannot print | Screen it first (§3) |
| Metallic, foil, neon, fluorescent | Not a thing in this process | — |
| Solid black across the whole label | Ink load, drying, cost | Keep coverage under 30% |
| Another company's logo or marks | Not ours to reproduce | Customer's own marks only |
| Cartoon characters, film, TV, sports, game or music imagery | Protected by their owners | Original artwork |
| Real people's faces or likenesses | Rights and consent | Original or abstract |
| Text smaller than 1.5 mm cap height | Will not hold on press | Larger, or cut the text |
| Lines thinner than 0.2 mm | Will break up or vanish | Thicker strokes |

## 3. Photographs and tonal imagery

A photo can appear, but it must be converted to a **1-bit dot screen** first —
black dots of varying size, no grey. We do that conversion; the customer just
supplies the photograph.

High-contrast, simple subjects screen well. Faces, busy backgrounds and
low-contrast images do not. Say so plainly rather than promising a good result.

## 4. The canvas

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

## 5. Elements we add ourselves

Every bottle carries these. **We add them. Do not design them, do not draw
them, and do not ask the customer whether they want them** — the answer is
always yes, and the versions we hold are the approved ones.

- **Nutrition Facts panel** — about 31 mm wide, full height of the label
- **Distributor and bottler block** — rotated 90°, beside the panel
- **Certification marks** — BPA Free, recycling, origin
- **Product descriptor** — e.g. PURIFIED WATER, and the volume
- **Social icons and website**, where the customer has them

Together these take roughly a quarter of the label, usually one end of it.

What this means for the artwork: plan it to occupy about three quarters of
the label, and treat one end as already full. A design that needs the whole
label will not work. A customer asking to remove the nutrition panel or the
certification marks is asking for something we cannot legally print — say so.

If the customer wants a QR code, their own logo, or their own social handles,
those *are* worth capturing in the brief, because we need the content from
them.

## 6. What works well

Observed across production jobs:

- Bold line drawings with consistent stroke weight
- Heavy condensed type for the main wordmark
- Circular badges and medallions
- A script accent used sparingly, for one or two phrases
- Zone-based layouts — distinct regions rather than one centred composition
- Ink coverage between 5% and 25%

## 7. What to produce

**Do not attempt the print file.** You do not have our templates, our
component library, our seam measurements or our fonts. Anything you generate
will look plausible and be unusable. Producing it wastes the customer's time
and ours.

Instead:

1. **Interview the customer.** Up to five short questions, one at a time:
   the subject, the mood, the motifs, any text or logo that must appear, and
   anything they want avoided.
2. **Correct them as you go** if they ask for something in §2.
3. **Optionally sketch one concept** so they can see the direction — black
   line work on white only. Label it clearly as a concept, not artwork.
4. **Finish with this JSON and nothing after it:**

```json
{
  "schema": "bottle-brief/1",
  "brand": "",
  "theme": "one or two sentences describing the artwork",
  "technique": "line_art | halftone | type_led",
  "required_text": [],
  "motifs": [],
  "mood": [],
  "avoid": [],
  "notes": ""
}
```

The customer pastes that back into our form. That is the handoff.
