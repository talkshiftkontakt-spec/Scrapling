# Exercise Scraper (PL + EN)

Narzędzie do wyszukiwania i scrapowania ćwiczeń gramatycznych z internetu w wersji **polskiej** i **angielskiej**, zbudowane na [Scrapling](https://github.com/D4Vinci/Scrapling).

Dostępne jako **CLI**, **API** oraz **aplikacja webowa**.

## Co robi

1. Buduje zapytania wyszukiwania (PL / EN / oba)
2. Zbiera URL ze stron z ćwiczeniami
3. Pobiera strony przez Scrapling Spider (z poszanowaniem `robots.txt`)
4. Wyciąga pojedyncze zadania heurystykami
5. Zapisuje wynik na dysk i w bazie SQLite

## Instalacja

```bash
# Z katalogu głównego repozytorium Scrapling
pip install -e .
pip install -e "examples/exercise-scraper[api,dev]"
cd examples/exercise-scraper/frontend && npm install
```

Opcjonalnie SerpAPI (stabilniejsze wyszukiwanie):

```bash
pip install -e "examples/exercise-scraper[search]"
export SERPAPI_KEY=your_key
```

## Aplikacja webowa

### Szybki start (jeden terminal)

```bash
./examples/exercise-scraper/scripts/start.sh
```

### Ręcznie (dwa terminale)

```bash
# Terminal 1: API
./examples/exercise-scraper/scripts/run-api.sh

# Terminal 2: UI
./examples/exercise-scraper/scripts/run-web.sh
```

Otwórz `http://localhost:3000`.

Jeśli wejdziesz na `http://localhost:8000`, zobaczysz tylko stronę backendu i linki do API. To nie jest główny interfejs aplikacji.

Frontend przekierowuje `/api/*` do backendu (port 8000), więc nie musisz ręcznie ustawiać `NEXT_PUBLIC_API_URL` w przeglądarce.

### Rozwiązywanie problemów

| Problem | Rozwiązanie |
|---------|-------------|
| „Brak połączenia z API” | Uruchom `run-api.sh` lub `start.sh` |
| Pusty wynik zadań | Zwiększ limit stron (np. 15), spróbuj innej frazy |
| `ModuleNotFoundError` | `pip install -e . && pip install -e "examples/exercise-scraper[api]"` |
| `npm run dev` nie działa | `cd frontend && npm install` |

### API

| Endpoint | Opis |
|----------|------|
| `GET /api/health` | Status serwera |
| `POST /api/jobs` | Uruchom zbieranie |
| `GET /api/jobs` | Lista zadań |
| `GET /api/jobs/{id}` | Status zadania |
| `GET /api/jobs/{id}/urls` | Znalezione strony |
| `GET /api/jobs/{id}/exercises` | Zebrane ćwiczenia |

## CLI

```bash
# Obie wersje językowe (domyślnie)
exercise-scraper "Past Simple" --lang both

# Tylko polskie źródła
exercise-scraper "czas Past Simple" --lang pl --max-pages 20

# Tylko angielskie
exercise-scraper "Past Simple" --lang en

# Podgląd URL-i bez scrapowania
exercise-scraper "Present Perfect" --lang both --dry-run

# SerpAPI zamiast DuckDuckGo
exercise-scraper "Past Simple" --provider serpapi
```

### Flagi

| Flaga | Opis |
|-------|------|
| `--lang` | `pl`, `en`, `both` (domyślnie: `both`) |
| `--max-pages` | Maks. liczba URL-i (domyślnie: 40) |
| `--output` | Katalog wyjściowy (domyślnie: `output/`) |
| `--delay` | Opóźnienie między requestami w sekundach |
| `--min-confidence` | Próg jakości ekstrakcji 0.0–1.0 |
| `--provider` | `duckduckgo` (bez klucza) lub `serpapi` |
| `--topic-en` / `--topic-pl` | Nadpisanie frazy per język |
| `--dry-run` | Tylko lista URL-i |
| `--verbose` | Szczegółowy log |

## Struktura wyjścia

```
output/past-simple_2026-07-07/
├── manifest.json          # meta crawla
├── exercises.json         # wszystkie zadania
├── exercises_pl.json      # tylko PL
├── exercises_en.json      # tylko EN
├── pages/                 # Markdown per źródło
│   └── 001_example-com.md
└── report.txt             # podsumowanie
```

## Zmienne środowiskowe

```env
SERPAPI_KEY=...
EXERCISE_SCRAPER_MAX_PAGES=40
EXERCISE_SCRAPER_DELAY=1.5
EXERCISE_SCRAPER_MIN_CONFIDENCE=0.4
```

## Ograniczenia (MVP)

- Nie przeszukuje dosłownie całego internetu — tylko wyniki wyszukiwarki
- Ekstrakcja opiera się na heurystykach (różny HTML na każdej stronie)
- Strony za paywallem / logowaniem mogą nie działać
- Używaj treści wyłącznie do celów edukacyjnych; respektuj prawa autorskie

## Testy

```bash
cd examples/exercise-scraper
pytest -q
```

## Architektura

```
exercise_scraper/       # silnik scrapowania
backend/                # FastAPI + SQLite
frontend/               # Next.js UI
scripts/                # run-api.sh, run-web.sh
```

## Roadmap

- [ ] Reguły per domena (`domain_rules.yaml`)
- [ ] Obsługa PDF (`pdfplumber`)
- [ ] LLM fallback dla trudnych stron
- [ ] Eksport do Anki CSV
