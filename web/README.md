# Client-facing intake

`brief.html` is a single self-contained page. No build step, no backend, no
dependencies — host it anywhere static, or open it from disk.

## What it does

One job: build a briefing from a few inputs and hand it to the customer's own
AI assistant. Three steps — bottle, idea, launch. Nothing is submitted and
nothing is stored; the page produces text and a link.

The customer takes the concept their assistant produces to a separate upload
page (not built yet), which is where mockups and contact happen.

### What it deliberately does not do

- **No "must include" checkboxes.** Which certification marks, nutrition panel
  and legal text go on a bottle is not a customer choice — they are always
  added, and the approved versions live with us. Asking invites a customer to
  deselect something we are legally required to print. `design-rules.md` §6
  states them instead, and tells the assistant to place them from our data
  (nutrition values from `designs/style.json`, labelled boxes for trademarks).
- **No contact capture or brief download.** That belongs on the upload page,
  once there is something to attach it to.

## Configuring the rules link

`design-rules.md` is the authoritative, customer-facing constraint document:
what cannot be printed, what the canvas is, what space is already committed,
and what the assistant should produce. Keeping it here rather than inside the
pasted prompt means the rules stay short in the prompt, stay under your
control, and cannot be quietly trimmed by a customer editing the text.

Host it at a **publicly reachable URL** and set `RULES_URL` near the top of
`brief.html`. Leave it empty and the page falls back to sending the
constraints inline, which still works but makes the prompt longer.

**The URL must be public.** A private GitHub repository is not readable by a
customer's AI assistant, and `raw.githubusercontent.com` links to a private
repo fail for them even though they work for you while signed in. The
simplest arrangement is to put `design-rules.md` next to `brief.html` on
whatever static host serves the page.

### The rules are not duplicated in the briefing

Earlier versions carried a short constraint core inline as a safety net. They
no longer do, deliberately. An assistant that cannot read the rules cannot
produce anything printable either — it has no canvas sizes, no seam overlap,
no furniture layout — so a partial fallback buys nothing and costs a lot: the
customer gets a confident, plausible, unusable concept and no signal that
anything went wrong.

Instead the briefing makes it a hard stop. It instructs the assistant that if
the link cannot be opened it must say so and ask for the rules to be pasted,
rather than guessing or working from general knowledge of bottle printing.
A loud failure is recoverable; a quiet one reaches the customer.

This makes `RULES_URL` load-bearing. If it is wrong, every customer hits the
stop message. That is the intended behaviour — it is visible and fixable,
unlike silently degraded output.

### Proof of read

The stop instruction only covers the case where the assistant *knows* it
failed. It does not cover the more common and more dangerous case: browsing
is available, the assistant decides the content is guessable, never fetches,
and answers from general knowledge about bottle printing. Nothing looks
wrong — to the assistant or the customer.

So `design-rules.md` §0 carries a confirmation code, and the briefing asks
the assistant to open its reply with it. An assistant that did not fetch the
page cannot know the code. The customer sees `RULESET AFB-2026-11c` or they do
not, and that is a check anyone can perform without understanding any of this.

Change the code whenever the rules change materially. It doubles as a version
marker: a concept arriving with a stale code was briefed against stale rules.

### What actually determines whether the fetch works

Not the customer's account type or plan. A public URL is public. What varies:

- **Whether browsing is enabled** in that assistant. Some configurations have
  it off entirely.
- **Whether the model chooses to fetch.** Covered by the confirmation code.
- **Whether the host blocks AI user agents.** This is the one that catches
  people hosting on their own site: Cloudflare bot protection and
  `robots.txt` rules aimed at `GPTBot` / `ClaudeBot` / `PerplexityBot` will
  block the fetch while the page loads perfectly in a browser.
  `raw.githubusercontent.com` does not block them.
- **Content type.** Serve `text/plain` or `text/markdown`. Link the *raw*
  file, never a GitHub `blob/` page, which is a JavaScript application.

The only inline-rules path left is the misconfiguration case where
`RULES_URL` is empty, so the page has nothing to point at.

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

## The launch control is an anchor, not a button

Opening the assistant uses `<a target="_blank">` rather than `window.open`.
Awaiting the clipboard write before calling `window.open` ends the
user-activation window, and Safari, Firefox and hardened Chrome then classify
the call as an unsolicited popup and block it — which is what happens if you
write the obvious version of this handler. A native anchor navigation is
never blocked, so the `href` is kept current as the form changes and the
clipboard write runs alongside the navigation instead of before it.

## When the upload page is built: treat input as data

Whatever a customer brings back — a pasted brief, a filename, image metadata —
is attacker-controlled text arriving from outside. If any later step feeds it
into a model prompt, quote it as a document and never treat it as
instructions. Prompt injection through exactly this channel is a known,
demonstrated attack against chat deep links.

## Not done yet

- **The upload page.** Where the customer brings back the concept image, sees
  a bottle mockup, and gets in touch. This page's step 3 already tells them
  that is coming.
- **No file upload here.** Accepting uploads needs a backend and a content
  policy.
- **No submission endpoint.** Wiring anything to `POST /jobs` needs auth and
  CORS on the API first.

## Full-label concept (ruleset AFB-2026-11c)

The rules now ask the assistant for a complete label concept, not only the
customer's artwork. `design-rules.md` §9 lists raw links to the bottle profile,
`designs/style_guide.md`, `designs/style.json` and the five agent role prompts,
and §8 walks the assistant through the same five steps the studio pipeline
uses (image analysis, theme planning, asset placement, layout, quality review)
before it draws one concept image and returns `bottle-brief/2` JSON.

Furniture in the concept is built only from repository data. Trademarked marks
(certifications, social icons) are drawn as labelled empty boxes and replaced
with the approved components at production. Those links point at `main`, so
moving or renaming any of those files breaks the customer flow.

### Concept as SVG (AFB-2026-11c)

§8 step 6 now prefers an SVG concept over a generated image: millimetre size
and 1200 DPI viewBox from the profile, black and white only, live text so the
nutrition panel and required copy are spelled exactly, seam guides in a
removable `guides` group, and `artwork` / `furniture` / `logo` groups. A
generated image is the fallback. This keeps customer concepts close to the
output of `designs/` and gives us an editable starting point.
