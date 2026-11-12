# Client-facing intake

`brief.html` is a single self-contained page. No build step, no backend, no
dependencies — host it anywhere static, or open it from disk.

## What it does

Collects a structured artwork brief from a client and emits it as JSON
conforming to `bottle-brief/1`, which maps onto the API's `POST /jobs` body.

The page has four steps. Steps 1, 2 and 4 are an ordinary form. Step 3 is
optional: it hands the client a pre-written briefing and opens ChatGPT or
Claude so they can think the idea through, then reads the assistant's reply
back into the form.

## Why the AI step works the way it does

**Clipboard first, link second.** Neither ChatGPT nor Claude documents a
prompt-prefill URL parameter as a supported integration. ChatGPT's `?q=`
works but is undocumented. Claude's `?q=` broke in October 2025
(anthropics/claude-code#8827) and was only resolved that November. Anthropic
*does* document a desktop deep link (`claude://claude.ai/new?q=`), but that
requires the desktop app.

So the page always copies the briefing to the clipboard before opening the
tab. If the prefill works, the client sends it. If it silently fails, they
paste. Either way the briefing is not lost. Over ~7500 characters the page
drops the parameter entirely and opens the bare site, because long URLs get
truncated unpredictably.

**The assistant writes a brief, not artwork.** The briefing says so
explicitly. The client's chat session has none of this repository — no
profiles, no seam overlap, no components. Asking it for a print file would
produce something unusable that looks plausible.

## Pasted content is data, not instructions

`extractJson` parses the client's paste and uses it to populate form fields.
Nothing in it is executed, and nothing is forwarded to a model as a command.

This matters: a brief is attacker-controlled text arriving from outside. If a
later processing step feeds briefs into a model prompt, treat the brief as a
quoted document and never as instructions — prompt injection through exactly
this channel is a known, demonstrated attack against chat deep links.

## Download behaviour

Inside the Claude artifact viewer a plain `<a download>` silently does
nothing; the page must call the `downloads` capability. Served from an
ordinary web server that capability is absent and the anchor works. `saveFile`
resolves the capability once and falls back, so the same file works in both
places. Copy-to-clipboard works everywhere and is the reliable path.

## Schema

```json
{
  "schema": "bottle-brief/1",
  "brand": "...", "profile_id": "fat_500ml",
  "bottle": {"name", "capacity_ml", "label_mm", "safe_print_width_mm", "canvas_px", "dpi"},
  "theme": "...", "technique": "line_art|halftone|type_led",
  "required_text": [], "components": [], "notes": "...",
  "contact": {"name", "email"},
  "print": {"inks": 1, "ink": "black", "substrate": "clear bottle", "white_ink": false}
}
```

`brand`, `theme`, `contact.name` and a valid `contact.email` are required;
the page will not emit a brief without them.

## Not done yet

- No file upload. Logos and references are requested by email. Accepting
  uploads needs a backend and a virus/content policy.
- No submission endpoint. The page produces a file; wiring it to `POST /jobs`
  needs the API to have auth and CORS first.
- `components` are slugs chosen by checkbox; they are not validated against
  the extracted component library until the job reaches the API.
