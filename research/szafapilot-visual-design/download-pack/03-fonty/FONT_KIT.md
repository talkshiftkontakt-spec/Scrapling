# Font kit — Szafapilot (anty-generyczny)

**Cel:** wyglądać jak produkt z własnym charakterem, nie jak template z Framer „AI SaaS”.

---

## Zasada nadrzędna

1. **Display ≠ UI** — inny krój (albo mocno inny weight/optical size) na H1 vs body.
2. **Unikaj Inter jako brand fontu.** Inter może zostać tylko w produkcie/app UI, nie na marketingu.
3. **Max 2 rodziny + opcjonalnie mono.** Trzecia rodzina = szum.
4. Licencja: sprawdź commercial / web embedding przed produkcją.

---

## Rekomendowane pary (konkret)

### Para 1 — „Soft Instrument” (jasny B2B, bezpiecznie premium)
| Rola | Font | Dlaczego |
|---|---|---|
| Display / H1 | **Satoshi** (Fontshare) lub **Switzer** (Fontshare) | geometryczny, nie Inter |
| Body / UI | **General Sans** (Fontshare) lub **Source Sans 3** (Google, OFL) | czytelny, spokojny |
| Mono (dane, ID, kod) | **IBM Plex Mono** lub **JetBrains Mono** | techniczny sygnał bez „hacker aesthetic” |

**Unikaj w tej parze:** Geist jako jedyny font (robi się zbyt Vercel-clone).

### Para 2 — „Editorial Craft” (najmocniej anti-slop)
| Rola | Font | Dlaczego |
|---|---|---|
| Display | **Instrument Serif** (Google) lub **Newsreader** / **Fraunces** | serif = natychmiastowa różnica vs AI SaaS |
| Body / UI | **Satoshi** lub **Manrope** (ostrożnie — Manrope bywa overused) | kontrast serif/sans |
| Mono | **IBM Plex Mono** | rzadziej niż JetBrains w marketingu |

**Referencje mood:** Granola, Arc/Dia, Intercom (editorial media).

### Para 3 — „Precision Void” (ciemny, pro-tool)
| Rola | Font | Dlaczego |
|---|---|---|
| Display | **Geist** (Vercel) **albo lepiej** **Cabinet Grotesk** / **PP Mori**-like → **Outfit** tylko jeśli nie masz budżetu | tight tracking, ostry |
| Body | ten sam grotesque w Regular/Medium | spójność |
| Mono | **Geist Mono** lub **Berkeley Mono** (płatny) / **Commit Mono** | stack wygląda „dev” |

**Uwaga:** czysty void + Geist = łatwo wpaść w Vercel/Linear clone. Dodaj **warm near-black** (`#0F0E0C`) jak Cursor, nie `#000`.

### Para 4 — „Agent Canvas” (AI, ale nie rainbow)
| Rola | Font | Dlaczego |
|---|---|---|
| Display | **Söhne**-like → **Satoshi** / **Switzer** | spokojny, produktowy |
| Body | **Source Sans 3** | neutralny |
| Mono | **JetBrains Mono** (tylko w composerze / meta agenta) | sygnał „tool” |

---

## Skale typograficzne (desktop)

| Token | Soft Instrument | Editorial | Precision |
|---|---|---|---|
| `--font-display-size` | 56–72px | 64–88px | 48–64px |
| `--font-display-weight` | 600–700 | 500–700 (serif) | 600–700 |
| `--font-display-tracking` | -0.02em … -0.04em | -0.01em … -0.02em | -0.03em … -0.05em |
| `--font-body-size` | 16–18px | 17–19px | 15–16px |
| `--font-body-leading` | 1.5–1.65 | 1.55–1.7 | 1.45–1.55 |
| `--font-nav-size` | 14px | 13–14px | 13–14px |

Mobile: H1 zwykle ×0.55–0.7 względem desktop.

---

## Skąd brać (legalnie)

### Darmowe / łatwe na start
| Font | Źródło | Licencja (sprawdź aktualną) |
|---|---|---|
| Satoshi, Switzer, General Sans, Cabinet Grotesk | [fontshare.com](https://www.fontshare.com) | Fontshare (commercial OK w typowych warunkach) |
| Instrument Serif, Newsreader, Fraunces, Source Sans 3, IBM Plex | Google Fonts | OFL |
| Geist / Geist Mono | [vercel.com/font](https://vercel.com/font) | SIL OFL |
| JetBrains Mono | JetBrains | OFL |

### Płatne (jeśli budżet — mocniejsza różnica)
| Font | Klimat |
|---|---|
| Söhne / Söhne Mono | Stripe-like precision |
| Neue Haas Grotesk | Shopify-like editorial grotesque |
| TWK Lausanne | Partiful / fashion-tech |
| Berkeley Mono | Linear-like mono |

---

## Czego NIE łączyć

- Instrument Serif + fioletowy mesh gradient = „AI editorial” klisz  
- Satoshi + pill CTAs + black/white + grain bez akcentu = „każdy SaaS 2024”  
- 3 display fonty na jednej stronie  
- Display serif w nawigacji i buttonach (zostaw serif na H1/H2)

---

## Szybki wybór dla Szafapilot

Jeśli nie chcesz myśleć długo:

1. **Marketing site:** Satoshi (H1) + Source Sans 3 (body) + IBM Plex Mono (rzadko)  
2. **Jeśli chcesz charakter:** Instrument Serif (H1) + Satoshi (UI)  
3. **App/dashboard:** Geist lub Satoshi + JetBrains Mono  

Potem dobierz **jeden** kierunek koloru z `04-kierunki/` — font bez decyzji koloru nadal może wyglądać generycznie.
