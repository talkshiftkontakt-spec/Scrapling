# Szafapilot — Visual Design Research Report

**Scope:** Visual design, layout, hierarchy, interaction, spacing, colour, typography, illustration, motion, and UX patterns only.  
**Out of scope:** Copywriting, messaging, SEO, product positioning, redesign proposals for live pages.  
**Method:** Aggressive Scrapling crawl of 30 priority product sites (DynamicSession + design-token extraction + viewport/full-page screenshots), followed by visual analysis of captured UI.  
**Date:** 2026-07-18  
**Product context:** Szafapilot (visual direction only; content ignored)

---

## 1. Research method

### 1.1 Crawl pipeline

| Step | Tooling | Output |
|---|---|---|
| Fetch + JS render | Scrapling `DynamicSession` (Playwright Chromium, `network_idle`) | Live DOM |
| Automation | Sync `page_action` | Cookie dismiss, viewport 1440×900 |
| Capture | Playwright screenshots | `*-viewport.png`, `*-full.png` |
| Design extraction | In-page JS evaluation | Colours, fonts, radii, shadows, sections, headings, buttons, nav, CSS vars |
| Aggregation | `design-token-aggregate.json` | Cross-site token summary |

Artifacts live under:

- `research/szafapilot-visual-design/screenshots/`
- `research/szafapilot-visual-design/raw/`
- `research/szafapilot-visual-design/crawl-summary.json`
- `research/szafapilot-visual-design/design-token-aggregate.json`
- `/opt/cursor/artifacts/szafapilot-visual-research/` (mirrored screenshots)

### 1.2 Corpus (30 / 30 successful)

**Premium SaaS:** Stripe, Linear, Notion, Vercel, Attio, Mercury, Ramp, Intercom, Supabase, Framer, Webflow, Relume  
**AI-native:** Perplexity, Clay, Cursor, Lovable, Granola, Raycast, Loom  
**Automation:** Zapier, Make, Retool, Airtable  
**E-commerce / marketplace:** Shopify, Canva, Partiful  
**Chrome extension / browser productivity:** Arc (Dia), Raycast Store  
**Dashboard products:** Datadog, Figma

Crawl result: **30 ok · 30 with design tokens · 30 with viewport screenshots**.

### 1.3 Aggregate signals (measured)

| Signal | Observation |
|---|---|
| Theme | **18 dark · 9 light · 3 unknown** (dark-majority among premium/AI/dev tools) |
| Dominant type families | Inter / Inter Variable / NotionInter / Geist / custom brand grotesques; mono accents (Berkeley Mono, Geist Mono, JetBrains Mono) |
| H1 scale (desktop) | Common band **48–96px**; outliers 26px (Cursor compact) → 112px (Partiful) |
| Button radius | Heavy use of **pill / near-pill** (`9999px` / stadium) or soft **8–16px** |
| Card radius | Typically **8–24px**; large hero “stage” containers often **24–40px+** |

---

## 2. Cross-site visual anatomy (what almost everyone does)

### 2.1 Header patterns

Recurring structure (left → right):

1. **Mark + wordmark**
2. **Primary nav** (3–7 items; dropdown chevrons common)
3. **Utility cluster:** Sign in (text) · secondary ghost · **primary solid pill**

Variants:

| Pattern | Examples | Visual notes |
|---|---|---|
| Floating pill nav | Raycast | Nav sits in a rounded floating bar, inset from edges |
| Announcement strip + nav | Ramp, Attio, Make, Airtable, Relume | Thin top bar for product news; often black or brand accent |
| Transparent-over-media | Mercury, Shopify, Partiful | White type; glass / outline CTAs |
| Social proof in header | Supabase (GitHub stars) | Authority baked into chrome |

### 2.2 Hero structures (ranked by frequency in corpus)

1. **Centered stack** — badge → H1 → sub → dual CTA → product stage  
   *Notion, Attio, Lovable, Relume, Airtable, Loom, Raycast*
2. **Left text + right visual / product**  
   *Zapier, Make, Clay (text under illustration), Granola, Shopify*
3. **Asymmetric editorial** — oversized H1 left, body/CTA right, media band below  
   *Intercom, Figma, Vercel (icon-centric)*
4. **Product-as-hero** — UI mockup dominates fold  
   *Linear, Cursor, Framer, Attio, Ramp*
5. **Prompt-as-CTA** — input replaces signup button  
   *Lovable, Relume, Retool*
6. **Atmospheric full-bleed** — cinematic image, minimal UI chrome  
   *Mercury, Shopify, Partiful*

### 2.3 CTA systems

Almost universal dual-path:

| Role | Visual treatment |
|---|---|
| Primary | Solid high-contrast fill (black on light, white on dark, or single brand accent) · pill/stadium |
| Secondary | Ghost / 1px border / frosted glass · equal height to primary |
| Header echo | Same primary repeated top-right |

Accent CTA colours observed (single punch colour, not rainbow):

- Stripe purple · Ramp electric lime · Zapier orange · Make magenta · Supabase emerald · Loom/Webflow blue · Clay lime · Relume purple gradient

### 2.4 Product showcase styles

| Style | Examples | When it feels premium |
|---|---|---|
| Framed app window (macOS chrome optional) | Linear, Cursor, Framer, Granola | Soft diffuse shadow, large radius, subtle border |
| Floating / bento cards | Stripe modal, Ramp skeleton UI, Supabase feature bento | Varied card widths; restrained borders |
| Layered stack / fan | Figma | Overlapping cards with soft depth |
| Abstract 3D / metaphor | Clay, Make, Zapier | Tactile lighting; not stock icons |
| Lifestyle photography | Mercury, Shopify, Partiful, Loom | Full-bleed, mood first |
| Prompt UI as product | Lovable, Retool, Relume | Instant interaction metaphor |

### 2.5 Social proof styles

- **Monochrome logo clouds** (most common) — OpenAI/Figma/etc. stripped of brand colour  
- **Live / precision metrics** — Ramp ticker & percentage; Intercom scale claims via UI density  
- **Avatar clusters** — Notion hand-drawn faces  
- **Ratings pill** — Partiful stars  
- **GitHub stars in nav** — Supabase  

### 2.6 Footer (structural, not content)

Typical modern SaaS footer:

- Wide multi-column link grid  
- Brand column with mark  
- Legal / status / locale row  
- Often dark even on light sites (or inverted band)  
- Low visual weight; no heavy illustration

---

## 3. Site-by-site visual briefs

For each entry: URL · screenshot refs · strengths · premium cues · reusable patterns · avoidances.  
Screenshot paths are relative to `research/szafapilot-visual-design/`.

---

### 3.1 Premium SaaS

#### Stripe — https://stripe.com  
**Screenshots:** `screenshots/stripe-viewport.jpg`, `screenshots/stripe-full.jpg`  
**Fonts / theme:** Söhne (`sohne-var`) · dark atmospheric base · purple accent `#635BFF`

**Visually strong:** Atmospheric gradient “void” behind white floating stage; nested product cards (checkout + metric + dashboard); dual CTA (solid + outline); generous padding.  
**Feels premium:** Soft multi-hue glow, refined radius consistency (~6–16px), product UI treated as sculpture.  
**Reuse:** Floating white stage on dark gradient; metric card as visual proof; purple solid + purple outline CTA pair.  
**Avoid:** Over-busy mega-modals without a single focal product; rainbow gradients without a dominant brand hue.

#### Linear — https://linear.app  
**Screenshots:** `screenshots/linear-viewport.jpg`, `screenshots/linear-full.jpg`  
**Fonts / theme:** Inter Variable + Berkeley Mono · pure dark · near-monochrome

**Visually strong:** Left-aligned H1 (~64px), white pill Sign up, high-fidelity product window with subtle 1px borders; AI agent overlay as secondary float.  
**Feels premium:** Extreme restraint; depth via value shifts not heavy shadows; mono for code moments.  
**Reuse:** Dark product-in-hero; white capsule CTA; status colour used sparingly; mono accents.  
**Avoid:** Decorative gradients on Linear-like surfaces; multi-colour marketing chrome.

#### Notion — https://www.notion.so → notion.com  
**Screenshots:** `screenshots/notion-viewport.jpg`, `screenshots/notion-full.jpg`  
**Fonts / theme:** NotionInter + Lyon Text · light · Notion blue CTA

**Visually strong:** Centered hero; avatar cluster; hand-drawn lo-fi icons; huge H1 (~96px); product screenshot with soft shadow; greyscale logo row.  
**Feels premium:** Soft pastels + black type; illustration personality without clutter; enormous whitespace.  
**Reuse:** Centered free CTA; playful but sparse illustration; logo cloud under fold.  
**Avoid:** Dense icon grids; competing accent colours.

#### Vercel — https://vercel.com  
**Screenshots:** `screenshots/vercel-viewport.jpg`, `screenshots/vercel-full.jpg`  
**Fonts / theme:** Geist Sans + Geist Mono · pure black · luminous mark

**Visually strong:** Icon as luminous center; mono technical line; white/ghost dual CTA; monochrome customer logos.  
**Feels premium:** Void + rim light; grain; no fluff.  
**Reuse:** Luminous brand mark; mono accent line; absolute black/white CTA system.  
**Avoid:** Soft pastel AI mesh on a Vercel-like brand; coloured logo clouds.

#### Attio — https://attio.com  
**Screenshots:** `screenshots/attio-viewport.jpg`, `screenshots/attio-full.jpg`  
**Fonts / theme:** Inter · light greyscale+ · black CTAs

**Visually strong:** Announcement bar; centered hero; soft product window with subtle blue aura; dual CTA (ghost + solid black).  
**Feels premium:** Greyscale discipline; product UI does the colour work; airy spacing.  
**Reuse:** Black/white CTA pair; soft radial behind mockup; pill badges.  
**Avoid:** Neon accents on greyscale systems; card grids in the first viewport.

#### Mercury — https://mercury.com  
**Screenshots:** `screenshots/mercury-viewport.jpg`, `screenshots/mercury-full.jpg`  
**Fonts / theme:** Arcadia · dark cinematic photography · indigo CTA

**Visually strong:** Full-bleed landscape; glass pill email + CTA bar; minimal white nav.  
**Feels premium:** Art-directed photography; frosted controls; mood before features.  
**Reuse:** Atmospheric hero; glassmorphism form cluster; single accent CTA.  
**Avoid:** Stock office photos; busy chrome over photography.

#### Ramp — https://ramp.com  
**Screenshots:** `screenshots/ramp-viewport.jpg`, `screenshots/ramp-full.jpg`  
**Fonts / theme:** SF Pro / Lausanne · light + dot grid · electric lime CTA

**Visually strong:** Dot-grid canvas; email field + lime CTA; skeleton/floating UI fragments; live stats ticker.  
**Feels premium:** One neon accent against monochrome; technical texture; abstract product, not cluttered screenshots.  
**Reuse:** Dot grid; single electric accent; floating skeleton UI; realtime ticker.  
**Avoid:** Multiple neon accents; dense realistic dashboards in hero.

#### Intercom — https://www.intercom.com  
**Screenshots:** `screenshots/intercom-viewport.jpg`, `screenshots/intercom-full.jpg`  
**Fonts / theme:** Saans · light monochrome · electric blue tab accent

**Visually strong:** Asymmetric H1 + side body; moodboard media row; product peek below; AI chat float.  
**Feels premium:** Typography as hero; editorial media mix; sparse accent.  
**Reuse:** Asymmetric hero; mixed media strip; tabbed feature switcher.  
**Avoid:** Generic stock icon rows; equal-weight dual headlines.

#### Supabase — https://supabase.com  
**Screenshots:** `screenshots/supabase-viewport.jpg`, `screenshots/supabase-full.jpg`  
**Fonts / theme:** Inter + Source Code Pro · dark · emerald accent

**Visually strong:** Split hero; coloured second line in H1; bento feature cards; thin borders; wireframe illustrations.  
**Feels premium:** Dark matte surfaces; neon used surgically; card padding discipline.  
**Reuse:** Split-colour headline; bento with thin borders; mono in cards.  
**Avoid:** Thick card shadows; rainbow feature icons.

#### Framer — https://www.framer.com  
**Screenshots:** `screenshots/framer-viewport.jpg`, `screenshots/framer-full.jpg`  
**Fonts / theme:** Inter · pure black · blue Publish accent inside product

**Visually strong:** Product-as-hero with AI Agent panel visible; white primary CTA; large radius stage.  
**Feels premium:** True black; UI fidelity; AI interaction shown, not claimed visually.  
**Reuse:** Show the agent UI; white pill on black; soft stage radius.  
**Avoid:** Abstract AI blobs without product proof.

#### Webflow — https://webflow.com  
**Screenshots:** `screenshots/webflow-viewport.jpg`, `screenshots/webflow-full.jpg`  
**Fonts / theme:** WF Visual Sans · dark grain · Webflow blue

**Visually strong:** Centered H1; three feature cards with UI previews; blue announcement bar; greyscale logos.  
**Feels premium:** Grain texture; consistent radius; restrained blue.  
**Reuse:** Three-up preview cards; grain dark canvas; accent announcement.  
**Avoid:** Flat pure-black without texture when brand needs warmth.

#### Relume — https://www.relume.io → relume.ai  
**Screenshots:** `screenshots/relume-viewport.jpg`, `screenshots/relume-full.jpg`  
**Fonts / theme:** Relative · warm off-white · purple AI generate

**Visually strong:** Massive centered H1; floating side UI previews; gradient-border prompt; collaborative cursors.  
**Feels premium:** Soft canvas; AI input as hero; depth via soft shadows.  
**Reuse:** Prompt-as-CTA; floating side mockups; multiplayer cursors.  
**Avoid:** Hard purple-on-white cliché without custom type/canvas warmth.

---

### 3.2 AI-native products

#### Perplexity — https://www.perplexity.ai  
**Screenshots:** `screenshots/perplexity-viewport.jpg`, `screenshots/perplexity-full.jpg`  
**Note:** Crawl returned 403 for some requests but still captured a rendered surface (system UI / challenge). Treat as partially obstructed; supplement with known product patterns (centered search, dark/light calm UI, minimal chrome).

**Reuse (known product pattern):** Search/prompt as the entire product surface; quiet chrome.  
**Avoid:** Over-marketing chrome around a search-first product.

#### Clay — https://www.clay.com  
**Screenshots:** `screenshots/clay-viewport.jpg`, `screenshots/clay-full.jpg`  
**Fonts / theme:** Roobert · light sky → green landscape · claymorphic 3D

**Visually strong:** Hero illustration dominates; split text under art; lime CTA; tactile 3D.  
**Feels premium:** Custom 3D world; matte materials; confident colour pops.  
**Reuse:** Custom 3D metaphor; illustration-first hero; dual header CTAs.  
**Avoid:** Generic 3D icon packs; illustration that competes with CTA contrast.

#### Cursor — https://cursor.com  
**Screenshots:** `screenshots/cursor-viewport.jpg`, `screenshots/cursor-full.jpg`  
**Fonts / theme:** CursorGothic · warm dark · white pills · landscape under UI

**Visually strong:** Left H1 + OS-aware download CTA; multi-pane product window over soft landscape.  
**Feels premium:** Warm black (not pure void); artistic backdrop under technical UI; layered windows.  
**Reuse:** Product over atmospheric image; dual CTA (download + demo); warm dark.  
**Avoid:** Cold pure-black with no texture when brand wants human warmth.

#### Lovable — https://lovable.dev  
**Screenshots:** `screenshots/lovable-viewport.jpg`, `screenshots/lovable-full.jpg`  
**Fonts / theme:** Camera Plain Variable · dark mesh gradient · prompt bar hero

**Visually strong:** Aurora/mesh gradient; announcement pill; centered prompt as primary action.  
**Feels premium:** Soft luminous colour fields; floating input; high radius.  
**Reuse:** Prompt-first hero; mesh gradient atmosphere; New badge pill.  
**Avoid:** Harsh neon without blur; competing CTAs next to the prompt.

#### Granola — https://www.granola.ai  
**Screenshots:** `screenshots/granola-viewport.jpg`, `screenshots/granola-full.jpg`  
**Fonts / theme:** Melange (serif display) + Quadrant · warm off-white · lime accent

**Visually strong:** Serif H1; layered product window + call strip; abstract tech graphic.  
**Feels premium:** Editorial serif + soft canvas; lime used as edge accent; depth stacking.  
**Reuse:** Serif/sans pairing; layered mockup; soft eggshell ground.  
**Avoid:** Default Inter-only stacks when aiming for editorial distinctiveness.

#### Raycast — https://www.raycast.com  
**Screenshots:** `screenshots/raycast-viewport.jpg`, `screenshots/raycast-full.jpg`  
**Fonts / theme:** Inter · pure black · grainy red light streaks · floating pill nav

**Visually strong:** Symmetric center hero; dual platform downloads; abstract brand light.  
**Feels premium:** Noise/grain; extreme contrast; floating chrome.  
**Reuse:** Floating pill header; grainy brand light; dual OS CTAs.  
**Avoid:** Flat coloured backgrounds without texture; cluttered mid-hero widgets.

#### Loom — https://www.loom.com  
**Screenshots:** `screenshots/loom-viewport.jpg`, `screenshots/loom-full.jpg`  
**Fonts / theme:** Charlie · light · electric blue pills

**Visually strong:** Centered hero; large radius media stage with play affordance; dual CTAs including extension install.  
**Feels premium:** Soft off-white; confident blue; breathable vertical rhythm.  
**Reuse:** Media stage with play; extension CTA as secondary; large container radius.  
**Avoid:** Tiny video embeds; sharp rectangular media cards.

---

### 3.3 Automation tools

#### Zapier — https://zapier.com  
**Screenshots:** `screenshots/zapier-viewport.jpg`, `screenshots/zapier-full.jpg`  
**Fonts / theme:** Inter + DegularDisplay · warm light grey · orange accent

**Visually strong:** Split hero; abstract cascading blocks; email + Google dual signup; compliance micro-row; logo cloud.  
**Feels premium:** Warm canvas; orange used surgically; illustration as metaphor.  
**Reuse:** Dual auth CTAs; compliance chips; abstract automation art.  
**Avoid:** Rainbow connector logos flooding the hero.

#### Make — https://www.make.com  
**Screenshots:** `screenshots/make-viewport.jpg`, `screenshots/make-full.jpg`  
**Fonts / theme:** Inter · deep purple-black · magenta CTA + glow

**Visually strong:** Left copy / right blurred 3D disc; glass secondary CTA; muted logo row.  
**Feels premium:** Darkspace; glow on primary only; DOF blur on illustration.  
**Reuse:** Glow CTA; glass ghost button; abstract node metaphor.  
**Avoid:** Multiple glowing buttons; sharp stock screenshots in the same hero.

#### Retool — https://retool.com  
**Screenshots:** `screenshots/retool-viewport.jpg`, `screenshots/retool-full.jpg`  
**Fonts / theme:** Saans · dark floating stage · blue send control

**Visually strong:** Rounded dark stage; prompt composer; integration pills; blurred product film behind.  
**Feels premium:** Soft stage radius; AI composer as center; restrained accent.  
**Reuse:** Prompt composer hero; integration icon pills; film/product blur backdrop.  
**Avoid:** Dense form fields as first interaction.

#### Airtable — https://www.airtable.com  
**Screenshots:** `screenshots/airtable-viewport.jpg`, `screenshots/airtable-full.jpg`  
**Fonts / theme:** Haas · soft off-white · charcoal CTAs

**Visually strong:** Ultra-minimal centered hero; dual CTAs; almost no imagery above fold.  
**Feels premium:** Typography + whitespace as the entire system.  
**Reuse:** Extreme minimal hero; solid + ghost pair.  
**Avoid:** Empty minimalism without a later product proof section (Airtable relies on scroll).

---

### 3.4 E-commerce / marketplace software

#### Shopify — https://www.shopify.com  
**Screenshots:** `screenshots/shopify-viewport.jpg`, `screenshots/shopify-full.jpg`  
**Fonts / theme:** Neue Haas Grotesk · photo full-bleed · white CTAs · green mark only

**Visually strong:** Lifestyle photography; left-aligned hero type; white solid + outline play CTA; rounded black next-section stage.  
**Feels premium:** Brand green restraint; cinematic photo; large type.  
**Reuse:** Full-bleed photo hero; inverted white CTAs; soft section stage transition.  
**Avoid:** Green flooding the UI; clip-art product icons.

#### Canva — https://www.canva.com  
**Screenshots:** `screenshots/canva-viewport.jpg`, `screenshots/canva-full.jpg`  
**Fonts / theme:** Canva Sans · colourful / creative energy (dark capture in corpus)

**Visually strong:** Creative colour presence; product-forward creative tool energy.  
**Feels premium when:** Colour is organized into templates/grids rather than noise.  
**Reuse:** Colour as product capability signal; template grids.  
**Avoid:** Unstructured rainbow without hierarchy.

#### Partiful — https://partiful.com  
**Screenshots:** `screenshots/partiful-viewport.jpg`, `screenshots/partiful-full.jpg`  
**Fonts / theme:** TWK Lausanne · purple/blue gradient + party photo · huge H1 (~112px)

**Visually strong:** Split gradient/photo; floating invite card overlay; rating pill; soft blend edge.  
**Feels premium:** High-energy but controlled gradient; product UI floating on lifestyle.  
**Reuse:** Gradient/photo split; floating product card on photo; rating micro-proof.  
**Avoid:** Hard vertical splits; gradient + busy UI both fighting.

---

### 3.5 Chrome extensions / browser productivity

#### Arc / Dia — https://arc.net  
**Screenshots:** `screenshots/arc-viewport.jpg`, `screenshots/arc-full.jpg`  
**Fonts / theme:** Marlin Soft SQ (serif) · white center · grainy blue textured bands · scalloped edges

**Visually strong:** Serif headline; aura pastels; grainy textured colour bands; scalloped section edges; product window.  
**Feels premium:** Editorial + playful craft; texture; unique section geometry.  
**Reuse:** Grain texture bands; serif display; scalloped transitions; soft aura behind type.  
**Avoid:** Flat solid colour blocks without texture when aiming for Arc-like craft.

#### Raycast Store — https://www.raycast.com/store  
**Screenshots:** `screenshots/raycast-store-viewport.jpg`, `screenshots/raycast-store-full.jpg`  
**Fonts / theme:** Inter · dark · store/grid density

**Visually strong:** Extension marketplace density with Raycast dark system continuity.  
**Reuse:** Dark store grids; extension cards with icons + short meta.  
**Avoid:** Marketplace clutter without strong card rhythm.

---

### 3.6 Dashboard products

#### Datadog — https://www.datadoghq.com  
**Screenshots:** `screenshots/datadog-viewport.jpg`, `screenshots/datadog-full.jpg`  
**Fonts / theme:** NationalWeb · light · enterprise dashboard density

**Visually strong:** Enterprise clarity; product charts as proof; structured sections.  
**Feels premium when:** Data viz is clean and colour-coded by meaning.  
**Reuse:** Chart-as-proof; structured feature bands.  
**Avoid:** Screenshot dumps without cropping/focus.

#### Figma — https://www.figma.com  
**Screenshots:** `screenshots/figma-viewport.jpg`, `screenshots/figma-full.jpg`  
**Fonts / theme:** figmaSans · light canvas · black CTAs · colour only inside product cards

**Visually strong:** Asymmetric 3-zone hero; stacked colourful product cards; huge whitespace.  
**Feels premium:** Neutral chrome; creativity shown in artifacts; soft shadows.  
**Reuse:** Neutral shell + colourful product samples; detached large CTA.  
**Avoid:** Branding the whole page in rainbow.

---

## 4. Visual pattern library (by category)

### 4.1 Premium SaaS

| Pattern | Spec notes |
|---|---|
| Greyscale+ shell | White/off-white or black/charcoal; one accent only |
| Product stage | Large radius 16–40px; soft diffuse shadow; optional 1px border |
| Dual CTA | Solid primary + ghost secondary, same height |
| Logo cloud | Monochrome, low contrast, mid-weight |
| Announcement bar | 32–40px tall; dismissible; high contrast |

**Reference cluster:** Linear, Attio, Intercom, Stripe, Ramp

### 4.2 AI-native products

| Pattern | Spec notes |
|---|---|
| Prompt-as-hero | Large input ≥56px tall; pill radius; send control |
| Mesh / aurora ground | Soft multi-hue blur; low saturation behind text |
| Agent panel in mockup | Show thinking / tools / chat inside product |
| New badge pill | Small capsule above H1 |
| Grain / noise | Light film grain on dark gradients |

**Reference cluster:** Lovable, Relume, Retool, Cursor, Framer, Raycast, Clay

### 4.3 Automation tools

| Pattern | Spec notes |
|---|---|
| Flow metaphor art | Nodes, arcs, cascading blocks — not literal workflows first |
| Integration chips | Small logo pills under composer |
| Dual auth CTA | Email solid + Google outline |
| Compliance micro-row | Tiny icons + labels under CTAs |
| Darkspace or warm grey | Make dark · Zapier warm light |

**Reference cluster:** Zapier, Make, Retool, Airtable

### 4.4 Marketplace software

| Pattern | Spec notes |
|---|---|
| Emotional lifestyle hero | People/event imagery |
| Floating invite/product card | UI proof over photo |
| Gradient/photo blend | Soft feathered seam |
| Rating / social micro-proof | Compact pill near H1 |

**Reference cluster:** Partiful, Arc craft cues, Shopify social moments

### 4.5 E-commerce software

| Pattern | Spec notes |
|---|---|
| Full-bleed commerce photography | Overlay for type contrast |
| Brand colour sparingly | Logo/accent only |
| White CTA on dark media | Inverted high contrast |
| Rounded next-section stage | Soft transition into product story |

**Reference cluster:** Shopify, Canva (creative commerce), Ramp-like seller finance energy

### 4.6 Chrome extensions

| Pattern | Spec notes |
|---|---|
| Install / Download CTA OS-aware | Platform icons in pill |
| Store grid cards | Icon · title · short meta · radius 8–12px |
| Floating nav | Pill chrome (Raycast) |
| Extension secondary CTA | “Install Chrome Extension” as ghost |

**Reference cluster:** Raycast, Raycast Store, Loom extension CTA, Arc

### 4.7 Dashboard products

| Pattern | Spec notes |
|---|---|
| Cropped focused screenshots | One workflow, not whole app |
| Status colour semantics | Green/amber/red sparingly |
| Sidebar + canvas language | Familiar IA in mockups |
| Chart proof | Clean dataviz as social proof |

**Reference cluster:** Linear (app), Supabase bento, Datadog, Figma stacks, Attio

---

## 5. Trends 2025–2026

### 5.1 Most common layouts

1. Centered hero stack + product stage  
2. Left narrative / right visual  
3. Asymmetric editorial type  
4. Prompt composer as primary conversion surface  

### 5.2 Most effective hero structures (visual efficacy)

| Structure | Why it works visually |
|---|---|
| Product-as-hero (Linear/Cursor/Framer) | Instant comprehension of craft quality |
| Prompt-as-CTA (Lovable/Relume/Retool) | Interaction metaphor = modernity |
| Atmospheric photo (Mercury/Shopify) | Emotional premium without feature soup |
| Bento / multi-card (Stripe/Supabase) | Breadth without walls of text |

### 5.3 Modern typography choices

- **Custom grotesques** over default Inter clones when possible (Geist, Saans, Charlie, Relative, Roobert, CursorGothic)  
- **Serif display for differentiation** (Granola, Arc/Dia, Notion Lyon moments)  
- **Mono for technical credibility** (Vercel, Linear, Supabase, Attio)  
- **Tight tracking on large H1**; comfortable line-height on body  
- H1 desktop band typically **48–88px** for premium SaaS

### 5.4 Most premium visual systems

| System | Signature |
|---|---|
| Linear void | Near-black, 1px borders, white pill, mono accents |
| Stripe atmosphere | Soft multi-hue glow + white product sculpture |
| Attio greyscale+ | Neutral shell, product colour, black CTAs |
| Granola editorial | Serif + eggshell + lime edge |
| Raycast grain light | Noise, floating pill nav, stark CTAs |
| Mercury cinematic | Photo mood + glass controls |

### 5.5 Emerging patterns (2025–2026)

- **AI composer / prompt bar** replacing classic “Start free” as the visual focus  
- **Agent UI inside product mockups** (thinking states, tool traces, side panels)  
- **Film grain / noise** on dark gradients  
- **Warm dark** (Cursor) vs pure void (Vercel/Linear)  
- **Dot grids** and technical canvases (Ramp)  
- **Collaborative cursors** as decoration (Relume)  
- **OS-aware download CTAs**  
- **Live tickers / precision metrics** as motion social proof  
- **Scalloped / crafted section edges** (Arc) as anti-generic craft  
- **Skeleton UI** instead of dense realistic dashboards in heroes  

### 5.6 Outdated patterns to avoid

| Outdated | Why it reads dated |
|---|---|
| Purple-to-indigo generic AI gradient with Inter + white cards | Overused AI startup default |
| Heavy multi-layer drop shadows + skeuomorphic cards | Pre-2022 SaaS |
| Icon row of 6–8 features in the first viewport | Clutter; low premium signal |
| Bright illustrative mascot spam without craft | Toyish |
| Fully rounded “pill everything” with no sharp contrast | Soft but indistinct |
| Stock handshake / laptop photos | Non-specific |
| Rainbow logo clouds at full saturation | Visual noise |
| Autoscrolling logo marquee as sole proof | Commoditized |
| Glassmorphism everywhere | 2021–2022 fatigue unless restrained |
| Hero packed with stats, schedules, badges, chips | Dashboard-looking marketing |

---

## 6. Component-level design notes

### Colour

- Prefer **1 accent + neutrals**. Premium brands almost never use 3+ accents in chrome.  
- Dark themes: pure `#000` (Vercel/Linear/Raycast) **or** warm near-black (Cursor).  
- Light themes: prefer **off-white / warm grey** over pure `#FFF` (Zapier, Granola, Relume, Airtable).  
- Accent roles: CTA fill, active tab underline, AI sparkle — not body text.

### Typography

- Pair **display grotesque** with **optional mono**.  
- Editorial brands: **serif H1 + sans UI**.  
- Keep nav small and low contrast; let H1 own the fold.

### Grid & spacing

- Hero vertical rhythm: 24–40px between badge/H1/sub/CTA; 48–80px before product stage.  
- Content max widths commonly ~1100–1200px for type; product stages often full bleed with side padding 24–48px.  
- First viewport should feel **underfilled**.

### Cards, shadows, radius

- Borders: **1px low-contrast** > heavy shadows.  
- Shadows: large blur, low opacity, single layer.  
- Radius ladder: controls 8–9999px · cards 12–24px · stages 24–40px.

### Motion (observed / implied)

- Soft fade-ins of product stages  
- Gradient drift / grain shimmer  
- Prompt caret / thinking indicators  
- Live metric tickers  
- Parallax-light atmospheric photography  

Ship **2–3 intentional motions**, not continuous noise.

### Illustration

| Family | Examples |
|---|---|
| Claymorphic 3D | Clay |
| Abstract nodes / discs | Make, Zapier |
| Hand-drawn lo-fi | Notion |
| Wireframe technical | Supabase |
| None (type + product only) | Airtable, Attio, Linear |

---

## 7. Visual Direction Recommendation (for Szafapilot)

Five possible directions. **No copy. No headlines. No messaging.** Mood, colour, type, layout, interaction, and references only.

---

### Direction A — “Precision Void”

**Mood:** Calm, technical, high-signal, pro-tool seriousness.  
**Colour philosophy:** Near-black canvas; white primary actions; one cool accent (teal or cool green) used only for status/AI activity.  
**Typography philosophy:** Custom geometric grotesque + monospace for data/IDs; tight large display; quiet nav.  
**Layout philosophy:** Left-aligned or asymmetric hero; product window as primary visual; sparse sections; thin borders.  
**Interaction philosophy:** Subtle fades; status micro-motion; no mesh rainbows; OS/install or primary solid pill.  
**References:** Linear, Vercel, Cursor (structure), Framer (product fidelity), Supabase (accent discipline)

---

### Direction B — “Soft Instrument”

**Mood:** Approachable premium; light, airy, CRM/productivity calm.  
**Colour philosophy:** Warm off-white / soft grey shell; charcoal type; black CTAs; optional single pastel aura behind product.  
**Typography philosophy:** Refined grotesque (Inter-class or custom); medium H1 weight; excellent whitespace.  
**Layout philosophy:** Centered hero stack; floating product stage; monochrome logo cloud; dual CTA.  
**Interaction philosophy:** Soft shadow lifts; gentle scroll reveals; restrained hover borders.  
**References:** Attio, Notion, Airtable, Loom, Relume (structure without AI kitsch)

---

### Direction C — “Atmospheric Commerce”

**Mood:** Elevated, cinematic, human, marketplace/seller confidence.  
**Colour philosophy:** Photography-led neutrals; brand accent reserved for CTA/logo; dark overlays for type.  
**Typography philosophy:** Large clean grotesque on media; high contrast white type; minimal chrome.  
**Layout philosophy:** Full-bleed hero media; floating glass/inverted CTA cluster; rounded dark stages below.  
**Interaction philosophy:** Slow ken-burns / parallax-light; glass hover states; video play affordances.  
**References:** Mercury, Shopify, Partiful (energy control), Loom media stage

---

### Direction D — “Agent Canvas”

**Mood:** AI-native, generative, interactive-first, modern 2026.  
**Colour philosophy:** Dark or soft canvas; mesh/aurora **low saturation** under content; accent on Generate/Send only.  
**Typography philosophy:** Confident grotesque; optional small badge/ mono for “model/agent” meta.  
**Layout philosophy:** Prompt composer as hero focal; product/agent panel as proof; floating side artifacts optional.  
**Interaction philosophy:** Composer focus states; thinking indicators; gradient border pulse (subtle); avoid multiple competing CTAs.  
**References:** Lovable, Relume, Retool, Framer Agent panel, Perplexity (search-first philosophy)

---

### Direction E — “Editorial Craft”

**Mood:** Distinctive, memorable, anti-generic, cultured product taste.  
**Colour philosophy:** Eggshell or textured colour bands; one sharp accent (lime/cobalt); grain allowed.  
**Typography philosophy:** Serif display + sans UI pair; generous margins; typographic hierarchy as art.  
**Layout philosophy:** Split or layered mockups; crafted section edges/textures; fewer sections, stronger compositions.  
**Interaction philosophy:** Layered depth on scroll; tactile hover; intentional irregular geometry (scallops/edges) used sparingly.  
**References:** Granola, Arc/Dia, Intercom (editorial media), Clay (craft illustration), Raycast (grain light)

---

## 8. Direction selection guidance (visual only)

| If Szafapilot should feel… | Lean toward |
|---|---|
| Developer-grade / workflow precision | **A Precision Void** |
| Clean B2B SaaS default premium | **B Soft Instrument** |
| Seller / marketplace / human commerce | **C Atmospheric Commerce** |
| AI-first product interaction | **D Agent Canvas** |
| Differentiated brand craft | **E Editorial Craft** |

Hybrid note (visual only): **B + D** (soft shell + prompt composer) and **A + D** (void + agent panel) are the most common successful hybrids in this corpus.

---

## 9. Artifact index

### Crawl outputs

- `crawl_visual_research.py` — Scrapling crawler  
- `crawl-summary.json` — success matrix  
- `design-token-aggregate.json` — fonts, themes, H1 metrics, radii, colours  
- `raw/*.json` — per-site design tokens + snippets  
- `screenshots/*-viewport.png` — above-the-fold captures  
- `screenshots/*-full.png` — long-page captures (height-capped when extreme)

### Mirrored artifacts

`/opt/cursor/artifacts/szafapilot-visual-research/`

---

## 10. Closing note

This document is a **visual pattern research pack** for Szafapilot. It intentionally contains no marketing copy, no headline proposals, and no site redesign. Next implementation steps (when requested) should pick a direction from Section 7 and translate its colour/type/layout/interaction rules into a design system — still without inventing messaging in this research layer.
