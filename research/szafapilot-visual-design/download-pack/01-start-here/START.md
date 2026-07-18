# Szafapilot — paczka wizualna (do pobrania)

**Co to jest:** gotowa paczka researchu + praktyczne rekomendacje (czcionki, kolory, layout, anti-AI-slop).  
**Czego tu nie ma:** copywritingu, haseł, SEO, redesignu gotowej strony.

## Jak czytać (kolejność)

1. `01-start-here/START.md` — szybki przegląd
2. `02-anti-ai-slop/NIE_ROB_TEGO.md` — lista „wygląda jak AI”
3. `03-fonty/FONT_KIT.md` — konkretne pary fontów + skąd brać
4. `04-kierunki/` — 5 kierunków wizualnych (wybierz 1)
5. `05-tokeny-css/` — gotowe CSS variables pod wybrane kierunki
6. `06-checklisty/` — checklisty przed wdrożeniem
7. `07-screenshots-viewport/` — zrzuty 30 stron referencyjnych
8. `08-research/VISUAL_DESIGN_RESEARCH.md` — pełny raport badawczy

## Rekomendacja na start (Szafapilot)

Jeśli produkt ma wyglądać **premium i nie-generycznie**, wybierz jedną z dwóch ścieżek:

| Ścieżka | Kiedy | Folder |
|---|---|---|
| **B Soft Instrument + D Agent Canvas** | narzędzie B2B / AI workflow, jasny UI | `04-kierunki/B_soft_instrument.md` + `D_agent_canvas.md` |
| **E Editorial Craft** | chcesz mocno wyróżnić markę | `04-kierunki/E_editorial_craft.md` |

**Nie wybieraj domyślnie:** czarny void + fioletowy gradient + Inter + pill CTAs. To jest obecnie najczęstszy „AI look”.

## Zawartość techniczna

- `design-token-aggregate.json` — zmierzone fonty/kolory/radiusy z crawla
- `crawl-summary.json` — status 30/30 stron
- zrzuty JPEG viewport (skompresowane)

Data: 2026-07-18  
Metoda: Scrapling crawl + ekstrakcja tokenów + analiza wizualna
