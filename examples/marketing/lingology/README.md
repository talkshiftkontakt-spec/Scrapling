# Marketing pack — LingoLogy + LingoTutor

Pakiet research + content + instrukcje dla:

| Marka | URL | Dla kogo |
|-------|-----|----------|
| **LingoLogy** | https://www.lingology.pl | Dorośli → angielski 1:1 |
| **LingoTutor** | https://www.lingotutor.pl/welcome | Korepetytorzy → OS praktyki |

**Nie mieszaj CTA.** Kursant ≠ korepetytor. Szczegóły: [brand/positioning-matrix.md](brand/positioning-matrix.md).

---

## Co jest w środku

```
examples/marketing/lingology/
├── README.md                 ← jesteś tutaj
├── brand/
│   ├── lingology-brief.md
│   ├── lingotutor-brief.md
│   └── positioning-matrix.md
├── scrapes/
│   ├── INDEX-own.md
│   ├── lingology/ …
│   ├── lingotutor/ …
│   └── competitors/          # Preply, italki, BUKI, e-korepetycje, Cambly, TutorCruncher
├── content/
│   ├── hooks.md
│   ├── social-posts-lingology.md
│   ├── social-posts-lingotutor.md
│   ├── ugc-scripts-lingology.md
│   └── ugc-scripts-lingotutor.md
└── runbooks/
    ├── APPLY-PATCHES.md      # patche Scrapling → Twoje forki
    └── OPENSHORTS-PROMO.md   # od skryptu do wideo (bez VPS)
```

Integracje techniczne (OpenShorts / marketingskills / cloner): [`../integrations/`](../integrations/).

---

## Checklist — zrób Ty w ~30 minut

### Dziś (zero Dockera)

- [ ] Przeczytaj [brand/lingology-brief.md](brand/lingology-brief.md) + [brand/lingotutor-brief.md](brand/lingotutor-brief.md)
- [ ] Wybierz **1 hook** LL + **1 hook** LT z [content/hooks.md](content/hooks.md)
- [ ] Nagraj / wygeneruj 2 shorty ze skryptów UGC (folder `content/`)
- [ ] Opublikuj z captionami z `social-posts-*.md`

### Jak chcesz pełny OpenShorts

- [ ] [runbooks/APPLY-PATCHES.md](runbooks/APPLY-PATCHES.md) → OpenShorts
- [ ] [runbooks/OPENSHORTS-PROMO.md](runbooks/OPENSHORTS-PROMO.md) → klucze API + 2 URL-e

---

## Szybkie fakty (ze scrape 2026-07-15)

**LingoLogy**
- H1: *Angielski online dla dorosłych. Korepetycje 1:1 nastawione na mówienie.*
- Konsultacja **0 zł / 20 min** · lekcje **od 80 zł / 55 min**
- Diagnoza bariery + plan + LingoLogy App
- Target FAQ: dorośli 25–45, nie dzieci

**LingoTutor**
- H1: *Twój system operacyjny nauczania.*
- **Start 0 zł** · **Pro 59,99** · **Pro+ 99,99** / mies.
- Briefing AI rano · pętla post-lekcji 2 min · portal ucznia/rodzica
- Claim: 45 min adminu → 2 minuty

**Konkurenci zescrapowani:** Preply, italki, buki.org.pl, e-korepetycje.net, Cambly, TutorCruncher.  
(Superprof/Duolingo: blokada 403/SPA — notatka w `scrapes/competitors/INDEX.md`.)

---

## Co zrobił agent / czego nie

| Zrobione tu | Na Tobie |
|-------------|----------|
| Scrape LL + LT + konkurenci | Push patchy na forki (403 bota) |
| Brand briefs + positioning | Klucze Gemini / fal / ElevenLabs |
| 36 hooków, 20 postów, 10 skryptów UGC | Publikacja social |
| Runbooki bez VPS | Docker OpenShorts na PC jeśli chcesz |
