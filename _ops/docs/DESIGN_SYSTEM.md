# DigiVeritaz — Design System

The structural and art-direction reference for digiveritaz.com. Two audiences:

- **Building on this site** — follow it so new pages match what exists.
- **Handing to another project** — sections 2–9 transfer as a layout brief,
  section 10 as an art-direction brief. Colours, typefaces, logo and copy do
  **not** transfer; only structure, proportion and rhythm.

Every value below was read out of `site/css/style.css` and the live pages, not
invented. If the CSS changes, update this file.

The single rule everything else serves: **no section may read as a generic list
of bullet points.** If two consecutive sections share a silhouette, one of them
is wrong.

---

## 1. Tokens

Declared on `:root` in `site/css/style.css`. Never hard-code an off-scale value.

```css
--max:    1200px;                          /* container max width */
--radius: 14px;                            /* base card radius    */
--shadow: 0 10px 30px rgba(17,24,39,.08);
--border: #e5e7eb;
```

Colour and type tokens are deliberately omitted here — they are brand, not
system, and are the part that does not travel to another project.

---

## 2. Container and vertical rhythm

One container rule, used by every section:

```css
.container { max-width: var(--max); margin: 0 auto; padding: 0 20px; }
```

Sections are full-bleed so backgrounds run edge to edge; the `.container`
inside constrains content. **Never** put a max-width on the `<section>` itself.

Vertical padding uses three steps, not arbitrary values:

| Step | Use |
|---|---|
| `96px 0` | primary content sections — the default |
| `80px 0` | secondary / supporting sections |
| `60px 0` | compact strips: stats, marquee, trust bar |

Drop to `56px 0` below 780px. This rhythm is a large part of why the site reads
as designed rather than assembled.

**Gap scale** — `6, 8, 10, 12, 14, 16, 18, 22, 24, 30`.
Card grids use `16–24px`; tight metadata rows use `6–10px`.

**Radius scale** — `8, 10, 12, 14, 16, 18, 20, 22, 24` for surfaces,
`999px` for pills and chips, `50%` for icon bubbles and avatars. Airier cards
take the larger radii; dense list rows take the tighter ones.

---

## 3. Page rhythm

A long-form service page runs in this order. Each row is a **different layout
shape** — that alternation is the core of the design.

| # | Section | Shape |
|---|---|---|
| 1 | Hero | asymmetric 2-col `1.15fr .85fr`, copy left / composition right |
| 2 | Marquee | full-bleed dark scrolling band |
| 3 | Stats | 3–4 figures, vertical rules, no card borders |
| 4 | Trust | horizontal band of divided cells |
| 5 | Intro / positioning | asymmetric prose split |
| 6 | Process | **numbered vertical rows**, not cards |
| 7 | Platforms / core offering | 3-col card grid, centred, generous |
| 8 | Formats / capability | 3-col grid, denser, left-aligned |
| 9 | Measurement | 2-col split, list against panel |
| 10 | Industries | 4–6 col compact chip grid |
| 11 | Why us / differentiators | 2-col grid, larger text blocks |
| 12 | FAQ | single column, `max-width:820px`, accordion |
| 13 | Closing CTA | centred, constrained, one action |

Alternate section backgrounds with a subtle tint (`.alt`) on roughly every
other section, and add `border-top: 1px solid <faint>` where two same-coloured
sections meet.

---

## 4. Section header

Every section opens with the same three-part header. The repetition is
deliberate — it is the page's connective tissue.

```html
<div class="section-head">
  <span class="kicker">Two or three words</span>
  <h2>A full sentence with one <em>emphasised</em> phrase</h2>
  <p>One or two supporting sentences.</p>
</div>
```

```css
.section-head    { text-align:center; max-width:760px; margin:0 auto 48px; }
.section-head h2 { margin-bottom:14px; }
.section-head p  { max-width:620px; margin:0 auto; font-size:1.05rem; }
```

- **kicker** — uppercase, letter-spaced, 2–4 words, often with a leading dot
- **h2** — a *claim*, not a label. Wrap one phrase in `<em>` so the eye lands
- **lead** — sets up what follows; never restates the h2

Centre the header when the body is a grid; left-align it when the body is an
asymmetric split.

---

## 5. Grid patterns

| Pattern | Use |
|---|---|
| `repeat(3,1fr)` | primary card grids — the workhorse |
| `repeat(2,minmax(0,1fr))` | text-heavy cards needing room |
| `repeat(4,minmax(0,1fr))` | compact stats, logos, chips |
| `1.15fr .85fr` | hero — copy gets the larger column |
| `1.05fr .95fr` | near-even split with intentional asymmetry |
| `auto 1fr auto` | list rows: marker, body, trailing affordance |
| `1fr` | FAQ, prose, anything single column |

Use `minmax(0,1fr)` rather than `1fr` wherever cards may contain long unbroken
strings, or the grid overflows.

**Never use the same grid twice in a row.**

---

## 6. Card anatomy

Three weights. Pick by content density.

**Feature card** — generous, centred, for 3-col grids:

```css
padding: 44px 30px;  border-radius: 24px;  text-align: center;
border: 1px solid var(--border);  transition: .35s;
position: relative;  overflow: hidden;
```

Icon bubble (48–56px) → `<h3>` (1.2–1.35rem) → **2–3 sentences**. Not one line.

**Content card** — denser, left-aligned, for capability grids:

```css
padding: 28px 24px;  border-radius: 16px;  text-align: left;
```

Label or number → `<h3>` → paragraph → optional pill row.

**List row** — for process and comparison. *Not a card:*

```css
display: grid;  grid-template-columns: auto 1fr auto;
gap: 22px;  padding: 26px 0;
border-bottom: 1px solid <faint>;
```

Large muted number (`01`, `02` …) → body → trailing arrow. This is the main
device that stops the page becoming nothing but card grids.

**Hover** — every interactive card lifts:

```css
transform: translateY(-3px);
box-shadow: 0 14px 34px rgba(17,24,39,.09);
border-color: <accent at ~45% alpha>;
```

---

## 7. Signature components

**Eyebrow with status dot** — pill above every H1 and section heading:
`● SEO Growth System · Mumbai`. The most recognisable single element on the
site.

**Hero trust line** — one row of proof under the hero CTAs, separated by thin
rules: `★ 4.9 · 600+ Google reviews │ 120+ keywords on Page 1 │ Google Partner`.
Small, muted, factual — does more work than any hero image.

**Dual CTA, unequal weight** — one solid primary with a trailing arrow, one
ghost secondary pointing at an on-page anchor. Never two of equal weight.

**Dark marquee strip** — slow-scrolling full-bleed band on near-black carrying
short capability phrases separated by dots. Breaks up long light stretches.

**Stat band, not stat cards** — 3–4 large figures with thin vertical rules
between, no surrounding card. Reads as one instrument panel.

**Numbered process rows** — see §6.

**Hero side composition** — the hero's right column holds an abstract
arrangement of stacked mini-cards, not a stock photo. Marked `aria-hidden`.

---

## 8. Responsive

Breakpoints in order of importance: **1100, 1000, 900, 780, 600**.

| Width | Behaviour |
|---|---|
| 1100px | 4-col → 2-col; hero asymmetry starts flattening |
| 900px | 3-col → 2-col; asymmetric splits → `1fr` |
| 780px | single column throughout; section padding → `56px 0` |
| 600px | card padding tightens; chip rows wrap; type steps down |

Fluid type so headings scale without breakpoint jumps:

```css
h1 { font-size: clamp(2.2rem, 4.6vw, 3.9rem); }
h2 { font-size: clamp(1.7rem, 3.2vw, 2.4rem); }
```

**No horizontal overflow at any width.** Test at 390px.

---

## 9. Content density

The layout only holds up if the copy earns it.

- **Feature card** — heading + 2–3 full sentences. Four words inside 44px of
  padding looks broken.
- **Process row** — heading + 2 sentences on what actually happens.
- **Section lead** — 1–2 sentences that add information.
- **Headings are claims.** "Six platforms. Six distinct disciplines." not
  "Platforms". "What you get that most agencies skip." not "Benefits".
- **Vary section length.** Uniform length reads as a template.

If a section can only be filled with one-line bullets, it is the wrong section:
merge it into a neighbour or give it a different shape.

---

## 10. Art direction

**The one-line read:** a performance-marketing agency site that behaves like a
product site. Editorial confidence, real numbers everywhere, generous
whitespace, enough texture that nothing looks default. Serious, not corporate.
Dense, never cramped.

**It asserts, it doesn't describe.** Every heading is a sentence that could
start an argument.

**Numbers persuade.** Review counts, keyword positions, ROAS multiples, client
counts — in the hero trust line, the stat band, and inside cards. If a claim can
be a number, it is one. This is what makes the site feel earned.

**Texture, never flat fills.** Surfaces carry subtle gradients rather than solid
colour — a barely-there vertical wash on backgrounds, a directional 135°
gradient on accent elements and icon bubbles. Hairline borders separate
sections. A huge, very low-contrast wordmark sits in the footer as a texture
layer.

**Restrained motion.** `.2s`–`.35s`, `transform` and `shadow` only. Cards lift
3px with a softened shadow and accent-tinted border. One slow marquee provides
ambient movement. Nothing bounces, nothing slides in on scroll.

**Copy character.** Direct and slightly blunt — "Silence isn't a decision."
Specific over generic: name the platforms, tools, metrics, cities. Vagueness
reads as filler and breaks the effect entirely.

---

## 11. Anti-patterns

- Three-column card grids stacked back to back down the whole page
- Cards containing a single short line
- One-word category headings
- Identical vertical padding on every section — no rhythm
- Centred text inside a dense left-aligned list
- Icons with no copy, used as filler
- Spacing values outside the scale
- Any horizontal scrollbar on mobile

---

## 12. Build order

1. Set tokens — container, radius, shadow, spacing scale.
2. Build `.section-head` and the three card weights.
3. Lay out the page as **empty sections in the §3 order**, each with its
   distinct grid, before writing any copy.
4. Fill copy last, respecting §9.
5. Sweep responsive at 1100 / 900 / 780 / 600 / 390.

---

## 13. The test

Scroll the finished page at 25% zoom:

1. Can you tell where sections begin and end without reading?
2. Does any layout shape repeat twice in a row?
3. Is a real number visible in the first screen?
4. Does any card look empty inside its own padding?
5. Would a reader believe a person planned this?

Fail 2 or 4 → the layout is wrong. Fail 3 or 5 → the copy is wrong.
