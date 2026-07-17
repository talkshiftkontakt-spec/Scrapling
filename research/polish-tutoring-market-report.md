# Reverse Engineering the Polish Online Tutoring Market
## Comprehensive UX, CRO, SEO & Product Intelligence Report
**Date:** July 17, 2026 | **Market:** Poland + International Benchmarks

---

## Executive Summary

The Polish tutoring market exceeds **1 billion PLN annually**, growing 10–15% YoY. ~80% of parents pay for supplemental education (~950 PLN/month). English (35%) and mathematics (33%) dominate demand. The market splits into three archetypes:

| Archetype | Examples | Strength | Fatal Weakness |
|-----------|----------|----------|----------------|
| **Classifieds** | e-korepetycje.net, korepetycje.pl, korepetycje24.com | Massive supply, SEO, zero commission for students | No verification, no payments, no classroom, fake reviews |
| **Marketplaces** | BUKI, Superprof, Preply, TutoringPlatform | Matching, reviews, (some) payments | Hidden fees, subscription traps, tutor quality variance |
| **Managed schools** | Tutlo, Edualy, BUKI School | Full-stack learning, retention | Narrow subjects (Tutlo=English), contract friction, high price |

**Biggest market opportunity:** A Poland-first platform combining classifieds-scale supply with marketplace trust mechanics, exam-specific SEO, escrow payments, built-in classroom, and parent dashboards — at transparent pricing (no Student Pass, no credit expiry).

**User evidence anchor:** Trustpilot/forum data consistently flags: hidden subscriptions (Superprof), credit expiry (Preply), ghost tutors (classifieds), commission pain (BUKI tutors), contract cancellation (Tutlo/UOKiK), and lack of progress visibility (all marketplaces).

---

# PART 1 — COMPETITOR RESEARCH

## 1.1 Side-by-Side Positioning Matrix

| Platform | Target | UVP | Tone | Pricing Model | Trust Strategy |
|----------|--------|-----|------|---------------|----------------|
| **korepetycje.pl** | Parents, students, local tutors | "Najstarszy serwis" — 20+ years, 41k+ ads | Functional, legacy, no-nonsense | Free for students; tutors pay listing | Volume stats (90k tutors), longevity, blog |
| **e-korepetycje.net** | Same + SEO-driven discovery | Largest ad base (140k), exam content | Educational, community | Free browse; paid ad highlighting for tutors | Tutor testimonials, Facebook, blog SEO |
| **BUKI** | Parents seeking verified tutors | "Sprawdzony korepetytor" + lead gen | Professional, data-rich | Free contact; commission from tutors | Interview verification, review %, price tables |
| **Tutlo** | English learners (all ages) + B2B | On-demand English, TLE 360° method | Aspirational, family-friendly | Opaque packages; sales-led "Uzyskaj wycenę" | 4.5★ Trustpilot (4.4k), stats, tutor carousel |
| **Superprof PL** | Broad subjects, global | "Pierwsza lekcja za darmo" | Friendly marketplace | **Student Pass** (~49 USD/mo) + tutor rate | Reviews, identity check, 17k+ PL tutors |
| **Preply PL** | Language-first, global tutors | "100k tutors, 4.8 App Store" | Modern, confident | Subscription + prepaid lesson credits | Mass social proof, tutor cards, Ukraine support banner |
| **Edualy** | Exam prep families | "Gwarancja oczekiwanych wyników" | Warm, reassuring, exam-focused | From 85 PLN; packages; free trial | 8+ years, video testimonials, own classroom |
| **TutoringPlatform** | Full-stack online PL | Escrow, verified tutors, built-in video | Clean SaaS, trust-first | Pay-per-lesson; 10% commission | Escrow, 6h cancel, RODO, FAQ depth |
| **Wyzant** | US K-12 + test prep | Good Fit Guarantee — first hour free | Authority, results-driven | Pay-per-hour, no subscription | 4M reviews, university tutors, guarantee |
| **Varsity Tutors** | US premium tutoring | AI-enhanced, grade-level matching | Corporate, high-touch | Sales funnel; phone specialist | 98% satisfaction, 10M hours stats |
| **Tutorful** | UK parents | Hand-picked tutors, first lesson guarantee | Parent-safe, warm | From £20/h; platform payments | DBS checks, recorded lessons, 90% grade lift |
| **AmazingTalker** | Language learners (Asia) | 1 lesson minimum, no lock-in | Friendly, flexible | Per-lesson; tutor sets price | 3% tutor acceptance, AI ranking, escrow |
| **italki** | Language learners global | No subscription, pay-as-you-go | Community + marketplace | Per-lesson credits | Professional vs community tutor tiers |
| **Cambly** | English conversation adults | Native speakers 24/7 | Casual, lifestyle | Monthly subscription tiers | Native-only, app-first, progress tracking |
| **TeacherOn** | Global academic tutoring | Low commission tutor marketplace | utilitarian | Commission-based | Global reach, subject breadth |
| **Apprentus** | Lifestyle + academic EU | 130k teachers, any activity | Discovery, local | Free teacher signup; student pays tutor | City pages, activity taxonomy |

> **Note on korep.pl:** No major standalone domain found at scale in July 2026 research. Likely confusion with korepetycje.pl or shorthand. TutoringPlatform.pl positions as newer full-stack alternative with 10% commission vs industry 15–25%.

---

## 1.2 POLISH COMPETITORS — DEEP DIVE

### Korepetycje.pl

**Brand:** Legacy classifieds leader since 1998. 41,739 active ads, 90,686 registered tutors.

**Homepage Hero:**
- Headline: *"Znajdź korepetytora w Twojej okolicy"*
- Sub: *"Mamy 41739 aktywnych ogłoszeń!"*
- CTA: Search box (subject dropdown) — no prominent "book now"
- Visual hierarchy: Search → subject chips → dual CTA blocks (tutor join / student post ad)
- Social proof: Counter only — no reviews on homepage
- Trust: "20 lat", copyright 1998–2026
- Triggers: Scarcity via live ad count; dual-sided marketplace

**Navigation clicks:**
| Goal | Clicks | Notes |
|------|--------|-------|
| Find tutor | 0–1 | Homepage search |
| Book lesson | N/A | No booking — contact off-platform |
| Contact | 2–3 | Profile → contact |
| Pricing | 1 | Per-listing only |
| FAQ | 3+ | Under "Pomoc" |
| Registration | 2 | "Załóż konto" footer |

**Tutor profile:** Photo, bio text, subject, city, price, reviews (unverified), no calendar, no video, no badges, no availability sync.

**Booking flow:** Search → listing → register → message/call → arrange offline. **7–12+ clicks** to first lesson; payment off-platform.

**UX:** Dense subject taxonomy, minimal whitespace, legacy UI, weak mobile polish, no microinteractions, no empty-state design.

**CRO:** Primary CTA = search. Secondary = "Dołącz do nas" (tutor acquisition). No lead magnets, exit intent, guarantees, or refund policy on-site.

**SEO:** Strong on `/` + subject + city URL patterns. Blog exists. No visible schema. Title: brand + geo. Programmatic: cities × subjects. Weak exam landing pages.

**Features:** Search, filters (basic), reviews, blog, price comparator, student+tutor ads. Missing: payments, calendar, messaging quality, video, AI, dashboard.

---

### e-korepetycje.net

**Brand:** Largest Polish tutoring classifieds. 140k ads. SEO content machine.

**Homepage Hero:**
- 3-step onboarding: Register → Add/search → Schedule
- Popular subjects with counts (math 36,105; English 39,308)
- City grids with counts (Warsaw 31,973)
- Featured listings, blog, tutor success stories

**Trust:** Tutor-written testimonials (business growth stories). Facebook community.

**Navigation:** Similar to korepetycje.pl. Paid "wyróżnienie ogłoszenia" for tutors.

**Booking:** Off-platform. Messenger built-in.

**UX:** Better content hierarchy than korepetycje.pl. Blog drives SEO (matura, egzamin ósmoklasisty).

**CRO:** "Załóż darmowe konto" repeated. Social proof via tutor income stories (B2B acquisition).

**SEO:** **Best-in-class Polish tutoring SEO.** Article hub, news, exam timing content. Subject+city long-tail.

**User voice (forumszkolne.pl):** *"sporo jest ofert ale... jak przychodzi co do czego to cisza"* — many listings, poor response rate.

---

### BUKI Polska

**Brand:** Managed marketplace since 2014. Claims 130k+ tutors, 1.6M matches, 210k reviews.

**Homepage Hero:**
- Headline: *"Korepetycje dopasowane do Twoich potrzeb"*
- Filters: Subject, city, online toggle
- **"Sprawdzony korepetytor"** badge prominent
- Price orientation table: 50–70 PLN (student) → 100+ PLN (exam expert)
- Social proof: Per-tutor review counts, 97% positive on math category pages

**Navigation clicks:**
| Goal | Clicks |
|------|--------|
| Find tutor | 1 (homepage filters) |
| Book lesson | 3–4 (profile → contact → coordinator) |
| Contact | 1 ("Skontaktuj się — bezpłatne") |
| Pricing | 0 (on profile cards) |
| FAQ | 2–3 |
| Registration | 2 |

**Tutor profile:** Photo, name, rating, subjects, education, experience years, online badge, price, long bio, urgency copy ("ZOSTAŁY WOLNE MIEJSCA"), reviews, "Sprawdzony" badge.

**Booking:** Request → BUKI matches → tutor contact → off-platform or BUKI School. Commission from tutor side.

**UX:** Card grid, clear typography, trust badges, price transparency on cards. Weak: no instant booking, commission opacity for students.

**CRO:** "bezpłatne" contact, scarcity in bios, price anchoring tables, stats (130k tutors).

**SEO:** Excellent programmatic: `/korepetycje/{subject}/`, city variants, exam copy, FAQ blocks, price stats in copy.

**Trustpilot (4.5/302):** Students happy with matching. Tutors complain: **50% commission on 1–2 lessons**, vague student requests, profile blocks for lost students.

---

### Tutlo

**Brand:** Poland's largest **English-only** online school. 85k students, 4000+ tutors.

**Homepage Hero:**
- Headline: *"Nauka angielskiego online – kursy języka angielskiego w Tutlo"*
- Sub: Lifestyle flexibility, TLE 360°, no rigid schedules
- CTA: **"Uzyskaj wycenę"** / **"Wypróbuj Tutlo"** — sales-led, not self-serve
- Stats bar: 10+ lat, 80+ courses, 4000+ lektorów, 85,000+ uczniów
- Social proof: Testimonials, tutor carousel with "Prezentacja" video modals

**Navigation:** Segment by age (dzieci/młodzież/dorośli/firmy) + city SEO pages.

**Booking:** Sales call → package purchase → app login → on-demand tutor matching. **High friction** for price-sensitive users.

**UX:** Polished marketing site, heavy modals/popups (promo terms), app-centric. Trustpilot 4.5/4422.

**CRO:** Free trial lesson, promo discounts, parent-focused copy, exam course cards (ósmoklasista), "80% see progress" claim.

**Negative user voice (Trustpilot/naszeopinie):** Morning tutor shortage (time zones), **opaque cancellation costs**, UOKiK charges on contract terms, connection stability issues.

**SEO:** Strong on English + city ("kursy angielskiego Warszawa"). Narrow subject focus limits total TAM SEO.

---

### Superprof Polska

**Brand:** Global marketplace, 17k+ PL tutors, 1000+ subjects.

**Homepage:** Subject discovery, local + online, tutor cards.

**Pricing:** ~60 PLN/h average + **Student Pass subscription** (~49 USD/mo) to contact tutors. 97% offer first lesson free.

**Trust:** Identity verification claimed; reviews on profiles.

**Booking:** Browse free → subscribe to contact → arrange with tutor → pay tutor (often off-platform).

**UX:** Clean global template, good mobile, video on some profiles.

**CRO:** Free first lesson anchor, but Student Pass is **#1 churn driver**.

**Trustpilot pattern:** *"signed up to browse, charged $49, never contacted a teacher"* — bait-and-switch perception. Auto-contact requests to trigger billing.

**SEO:** `/lekcje/{subject}/{city}/` programmatic. Blog compares platforms (SEO capture).

---

### Preply (Poland)

**Homepage Hero (PL):**
- *"Ucz się szybciej dzięki najlepszym lekcjom języka"*
- Stats: 100k tutors, 300k 5★ ratings, 120+ subjects, 4.8 App Store
- Language chips with tutor counts
- 3-step how-it-works with tutor card previews
- Promise: *"Jeśli nie zaiskrzyło, wypróbuj innego lektora"*

**Pricing:** Tutor-set ($3–$40+ shown globally); **subscription + prepaid credits** that expire.

**Booking:** Select tutor → subscribe/pay bundle → schedule in classroom. ~5–7 clicks.

**UX:** Best-in-class marketplace UI. In-house classroom (controversial per user research — prefer Zoom).

**Trustpilot (4.3/21k):** AI support frustration, credit expiry, tutor no-shows, technical classroom failures.

**SEO:** City pages (Warszawa, Kraków), exam prep, native speaker geo pages. hreflang network.

---

### Edualy

**Brand:** Polish managed tutoring school. 8+ years. All school subjects.

**Homepage Hero:**
- *"Skorzystaj z pomocy naszych nauczycieli"*
- CTA: **"Zarezerwuj bezpłatną lekcję"**
- Pillars: Results guarantee, from 85 PLN, exam prep flow (3 steps)
- Own virtual classroom, lesson recording

**Booking:** Phone OR account → advisor/tutor match → package → schedule. Hybrid high-touch + self-serve.

**UX:** WordPress-style, warm illustrations, video testimonials, tutorial video.

**Trustpilot (4.5/68):** Strong when advisor responsive. Failures: **billing disputes on hour packages**, minimum top-up confusion.

**B2B:** Benefit Edualy — employer-funded monthly hour packages (4–6h).

**Differentiator:** Recorded lessons, family packages, no long contract (claimed).

---

### TutoringPlatform.pl

**Brand:** Newer full-stack Polish platform. **Best UX reference for greenfield.**

**Homepage Hero:**
- *"Znajdź korepetytora"* + mock student dashboard preview
- Dual CTA: Student / Teacher
- 4-step flow: Find → Book → Learn (built-in video) → Review
- Trust: Escrow, verified teachers, 6h cancel, 10% commission, RODO

**Features inventory:** Built-in HD video, interactive whiteboard, screen share, wallet (BLIK, PayU), escrow, parent accounts, ranking, intro video verification, no-show protection, 24h dispute window.

**Gap vs claim:** Smaller tutor supply vs classifieds. Marketing-heavy; needs user review validation at scale.

---

## 1.3 INTERNATIONAL BENCHMARKS — KEY PATTERNS

| Pattern | Wyzant | Tutorful | AmazingTalker | italki | Cambly |
|---------|--------|----------|---------------|--------|--------|
| First lesson guarantee | ✅ Good Fit | ✅ Free replacement | ✅ Transfer tutor | Trial lesson | Trial available |
| Subscription trap | ❌ | ❌ | ❌ | ❌ | ✅ Required |
| Built-in classroom | ❌ (tutor choice) | ✅ | Zoom | ✅ | ✅ Native |
| Vetting | Light | **DBS + 1-in-8** | 3% acceptance | Pro vs Community | Native-only |
| Parent features | Limited | Strong | Kids tier | Limited | Limited |
| Exam SEO | SAT/MCAT hubs | GCSE/A-Level | Local exam pages | Test prep tags | None |

**Transferable to Poland:** Tutorful's first-lesson guarantee + safeguarding; Wyzant's guarantee copy; AmazingTalker's pay-per-lesson; italki's no-subscription clarity; avoid Cambly/Preply credit expiry models.

---

# PART 2 — PSYCHOLOGY REVERSE ENGINEERING

## 2.1 Trust / Leave / Emotion Matrix

| Platform | Why trust? | Why leave? | Emotions | Objections removed | Objections remaining |
|----------|-----------|------------|----------|-------------------|---------------------|
| korepetycje.pl | 20-year legacy, huge choice, free | Ghost listings, no verification, scam risk | Hope → frustration | Cost (free browse), local choice | Safety, quality, convenience |
| e-korepetycje.net | SEO authority, tutor success stories | Same as classifieds + ad clutter | Curiosity, ambition | Price transparency in listings | Response rate, trust |
| BUKI | "Sprawdzony", reviews, price data | Commission inflates tutor prices; match quality | Relief (someone vetted) | "Is tutor real?" partially | Total cost, instant booking |
| Tutlo | Brand scale, 4.5★, method story | English-only, contracts, morning tutor gap | Aspiration, parental hope | "Will child speak?" | Price, lock-in, flexibility |
| Superprof | Free first lesson, breadth | **Student Pass shock** | Excitement → betrayal | Try before buy (lesson) | Hidden platform fee |
| Preply | Global tutors, slick UX | Credits expire, AI support | Confidence → trapped | Tutor choice breadth | Refunds, scheduling |
| Edualy | Human advisor, recordings, exam focus | Package billing disputes | Safety, structure | Exam anxiety | Price, autonomy |
| TutoringPlatform | Escrow, clear rules | New/unproven supply | Control, fairness | Payment safety | Tutor pool depth |

## 2.2 Psychological Principles Used (Cross-Competitor)

| Principle | Who uses it | How | Exploit opportunity |
|-----------|------------|-----|---------------------|
| **Social proof** | All | Review counts, stats, testimonials | Show *specific* outcomes ("matura +23 pkt") not generic 5★ |
| **Authority** | Tutlo, Edualy, BUKI | Method names, exam results, credentials | Verify credentials visibly; show CKE-linked outcomes |
| **Scarcity** | BUKI bios, Cambly promos | "Few slots left" | Use real availability data only — fake scarcity destroys trust |
| **Anchoring** | BUKI price tables, Tutlo packages | High anchor makes mid tier seem fair | Show "market average" then your fair price |
| **Loss aversion** | Preply credits, Superprof Pass | Sunk cost in subscriptions | **Never** — use "pause plan" instead |
| **Reciprocity** | Superprof, Edualy, Tutlo | Free first lesson | Extend: free 20-min diagnostic + study plan PDF |
| **Commitment** | Preply bundles, Tutlo contracts | Prepaid hours | Offer weekly billing with easy pause |
| **Choice architecture** | Preply filters, BUKI cards | Default sort by rating | Add "best match for your goal" AI default |
| **Progressive disclosure** | Varsity Tutors funnel | Grade level first | Goal → exam → level → budget → 3 matches |
| **Cognitive load** | Classifieds | Overwhelming choice | Curated shortlists of 3; decision in <3 min |

---

# PART 3 — USER RESEARCH (Public Sources)

## 3.1 Recurring Complaints (Polish + English)

| Source | Quote / Theme | Implication |
|--------|--------------|-------------|
| forumszkolne.pl | *"pełno ofert... jak przychodzi co do czego to cisza"* | Response-rate metric needed; penalize ghost profiles |
| Wykop | Tutor wanted phone top-up payment; unprofessional | In-platform payments mandatory |
| Trustpilot Superprof | Charged $49 without contacting teacher | Never charge before confirmed match |
| Trustpilot Preply | Credits expire; AI support loops | Simple refund policy; human escalation |
| Trustpilot Tutlo | Tutor availability gaps; cancellation costs | Clear cancel policy above fold |
| Trustpilot BUKI (tutors) | 50% fee on 1–2 lessons | Fair sliding commission |
| Trustpilot Edualy | Package hour minimum confusion | Transparent wallet UI |
| korepetytor.ai analysis | Fake reviews, ghost tutors, hidden fees | Verified reviews + escrow |
| Ranking Edukacji 2026 | Users want opinions with *specifics* not "polecam" | Structured review prompts |
| CBOS 2025/26 | 80% parents pay ~950 PLN/mo | Premium features for parents justify spend |

## 3.2 What Users Want (Selection Criteria)

1. **Polecenia** (word of mouth) — still #1 channel
2. Opinie z **konkretami** (exam score, behavior change)
3. **Lekcja próbna** before commitment
4. Clear **cel** (matura, ósmoklasista, zaległości)
5. Experience at **their level** (not generic)
6. **Online vs stationary** fit for child age
7. **Response speed** within 24h
8. Transparent **stawka** without surprise fees

## 3.3 Why People Stop Lessons

- No measurable progress after 4–6 weeks
- Personality mismatch (Wykop: "nie nadajemy na te same fale")
- Scheduling friction
- Price vs value disconnect
- Found cheaper direct (off-platform after marketplace intro)
- Exam completed — no retention hook

---

# PART 4 — SYNTHESIZED USER NEEDS

| Category | Recurring themes | Evidence strength |
|----------|-----------------|-------------------|
| **Trust** | Verification, real reviews, no scams, escrow | ★★★★★ |
| **Price** | All-in price visible; hate subscriptions & expiry | ★★★★★ |
| **Communication** | Fast tutor response; clear expectations pre-lesson | ★★★★☆ |
| **Booking** | Instant calendar; <5 clicks to confirmed lesson | ★★★★☆ |
| **Payments** | BLIK, escrow, invoices for parents | ★★★★☆ |
| **Scheduling** | Easy reschedule; reminders; timezone clarity | ★★★★☆ |
| **Tutor quality** | Subject expertise + pedagogy; exam track record | ★★★★★ |
| **Availability** | Real slots; morning PL tutors for languages | ★★★☆☆ |
| **Reviews** | Specific, verified, balanced (not all 5★) | ★★★★☆ |
| **Transparency** | Cancel/refund rules before payment | ★★★★★ |
| **Mobile** | Book + join lesson on phone | ★★★★☆ |
| **Search/Filter** | Exam type, price, availability same-day | ★★★★☆ |
| **Learning experience** | Whiteboard, recordings, materials | ★★★☆☆ |
| **Support** | Human help <24h; Polish language | ★★★★☆ |
| **Progress tracking** | Parent dashboard; pre/post assessments | ★★★★☆ |
| **Homework/Resources** | Between-lesson assignments | ★★★☆☆ |
| **Retention** | Goal milestones, streaks, exam countdown | ★★★☆☆ |
| **Gamification** | Light — Polish users skeptical of "games" | ★★☆☆☆ |

---

# PART 6 — MARKET GAPS

## What EVERY competitor does
- Tutor profiles with photo + bio + price
- Subject × location SEO pages
- Reviews (variable quality)
- Free first lesson or free contact (with catches)
- Mobile-responsive (uneven quality)
- English + math emphasis

## What ALMOST NOBODY does well
- **Verified exam outcomes** linked to CKE results
- **Guaranteed tutor response time** (SLA)
- **Parent progress dashboard** with plain-language summaries
- **Fair offboarding** — export your materials, pause not cancel
- **Polish exam-specific prep paths** (matura/ósmoklasista checklists per tutor)
- **Anti-ghost listing** enforcement on classifieds
- **Price transparency** including all fees upfront
- **Sibling/family wallet** with subject splitting

## Completely missing
- **Tutor reliability score** (response rate + show rate + punctuality)
- **School curriculum sync** (podstawa programowa tag per lesson)
- **Municipal/school partnership** channels
- **Refund insurance** for exam-prep packages
- **Neurodiversity-matched filtering** (ADHD, dyslexia) — barely exists in PL
- **UOKiK-transparent** contract terms as competitive feature

## Biggest market opportunity
**"Trust layer for Poland"** — combine e-korepetycje.net supply depth with TutoringPlatform escrow + Tutorful guarantees + BUKI-style exam SEO — **without** Superprof/Preply subscription traps.

## 10× Better vision
1. **Time-to-first-lesson < 10 minutes** (vs industry 2–7 days)
2. **Zero surprise charges** — one price on screen = price paid
3. **Guaranteed match** — 3 curated tutors in 60 seconds via goal wizard
4. **Exam outcome tracking** — mock scores over time
5. **Parent app** — approve bookings, see recordings, pay with BLIK
6. **Tutor CRM** — reduce ghosting, automate reminders
7. **Polish-first support** — human chat, not AI-only
8. **SEO moat** — 500+ exam × city × subject programmatic pages with unique data
9. **Retention loops** — post-exam upsell to next grade; sibling referrals
10. **B2B2C** — employer benefits (copy Edualy) with better UX

---

*Part 5 (1000 ranked ideas) continues in `polish-tutoring-ideas-ranked.md`*
