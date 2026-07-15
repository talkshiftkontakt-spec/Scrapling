# Runbook: promo video Lingology + LingoTutor w OpenShorts

Bez VPS — lokalnie na Twoim PC (Docker) albo samymi skryptami + API.

## A. Co już masz gotowe (bez OpenShorts)

W tym folderze marketingowym:

| Plik | Użycie |
|------|--------|
| [../content/ugc-scripts-lingology.md](../content/ugc-scripts-lingology.md) | 5 skryptów UGC → wklej do OpenShorts / CapCut / fal |
| [../content/ugc-scripts-lingotutor.md](../content/ugc-scripts-lingotutor.md) | j.w. dla tutorów |
| [../content/hooks.md](../content/hooks.md) | pierwsze 1–2 s filmu |
| [../scrapes/](../scrapes/) | surowy copy ze stron (research) |

Jeśli PC ledwo zipie: **nie odpalaj Dockera**. Weź skrypt UGC → Gemini (naprawa) → fal.ai (wideo) ręcznie.

## B. Pełny OpenShorts (po zastosowaniu patchy)

### 1. Patch + Docker

Zobacz [APPLY-PATCHES.md](APPLY-PATCHES.md) (sekcja OpenShorts), potem:

```bash
cd ~/projekty/openshorts
cp .env.example .env          # AWS opcjonalne
docker compose up --build
```

UI: **http://localhost:5175**

W `docker-compose` jest `SAASSHORTS_SCRAPE_MODE=static` — wystarczy dla obu stron.

### 2. Klucze w Settings

- `GEMINI_API_KEY` — https://aistudio.google.com/app/apikey  
- `FAL_KEY` — https://fal.ai  
- `ELEVENLABS_API_KEY` — https://elevenlabs.io  
- `UPLOAD_POST_API_KEY` — opcjonalnie (publikacja)

### 3. Wygeneruj 2 osobne filmy (nie mieszaj marek)

**Film A — LingoLogy (kursanci)**
1. Zakładka **AI Shorts**
2. URL: `https://www.lingology.pl`
3. Język: PL
4. Po wygenerowaniu skryptu — porównaj z `ugc-scripts-lingology.md` (możesz podmienić hook)

**Film B — LingoTutor (korepetytorzy)**
1. Nowy job
2. URL: `https://www.lingotutor.pl/welcome`
3. Pilnuj CTA: „Zacznij za darmo”, nie „umów konsultację”

### 4. Test scrapingu bez UI

```bash
python scripts/test_scrapling_scrape.py https://www.lingology.pl
python scripts/test_scrapling_scrape.py https://www.lingotutor.pl/welcome
```

Oczekiwane: HTTP 200, tysiące znaków tekstu, sensowny title.

## C. Publikacja

1. Pobierz klip z Gallery OpenShorts  
2. TikTok / IG Reels — caption z [../content/social-posts-lingology.md](../content/social-posts-lingology.md) lub `…-lingotutor.md`  
3. Osobne konta / osobne serie = mniej pomylenia buyer persona

## Troubleshooting

| Objaw | Fix |
|-------|-----|
| Pusty scrape | CLI test; jeśli &lt; 400 znaków → lokalnie `SAASSHORTS_SCRAPE_MODE=auto` + `scrapling install` |
| Brak Gemini | klucz w **Settings UI**, nie tylko `.env` |
| Docker za ciężki | użyj ścieżki A (skrypty UGC + fal ręcznie) |
