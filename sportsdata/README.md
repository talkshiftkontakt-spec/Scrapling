# SportsData Pipeline

Implementacja planu z `docs/sports-data-scraping-plan.md`.

## Co robi system

- **Faza 0**: synchronizacja przyszłych meczów piłki i tenisu z Flashscore
- **Faza 1**: statystyki przedmeczowe (forma, H2H, xG z Understat, best-effort SofaScore)
- **Faza 2**: snapshoty kursów z OddsPortal + modelowe kursy z Understat
- **Faza 3**: API, dashboard, monitoring jobów, historia rozegranych meczów

## Dwa tryby danych

| Tryb | Tabela | Co zawiera |
|---|---|---|
| **Nadchodzące mecze** | `events` + `event_stats_prematch` | forma, H2H, xG sezonowe *przed* meczem |
| **Rozegrane mecze (analiza)** | `match_results` | pełne statystyki *z* meczu: xG, strzały, kursy, tenis serwis/return |

## Instalacja

```bash
pip install -e ".[sportsdata]"
```

## Uruchomienie

```bash
# pełny pipeline (piłka: 45 dni, tenis: 14 dni)
sportsdata run-all

# węższe/szersze okno
sportsdata fixtures --days-ahead 30 --tennis-days-ahead 7

# pojedyncze joby
sportsdata fixtures
sportsdata stats
sportsdata odds
sportsdata backfill
sportsdata history    # Understat (5 sezonów) + football-data (12 lig × 5 sezonów) + archiwa WC/Euro/Grand Slam
sportsdata results    # ostatnie 90 dni rozegranych meczów ze statystykami Flashscore

# eksport JSON
sportsdata export --output data/upcoming.json

# API + dashboard
sportsdata serve --port 8080
```

## Endpointy API

- `GET /health`
- `GET /upcoming?sport=football|tennis`
- `GET /results?sport=football|tennis&league=Wimbledon`
- `GET /results/{id}`
- `POST /jobs/{fixtures_sync|stats_enrich|odds_snapshot|pre_match_boost|backfill|all}`
- `GET /dashboard/`

## Baza danych

Domyślnie SQLite: `data/sportsdata.db`

Tabele:
- `events`
- `event_stats_prematch`
- `odds_snapshots`
- `job_runs`
- `match_results` — rozegrane mecze ze statystykami (Understat, football-data, Flashscore)

## Historia rozegranych meczów (`history`)

Źródła importowane do `match_results`:

| Źródło | Zakres | Dane |
|---|---|---|
| **Understat** | EPL, La Liga, Serie A, Bundesliga, Ligue 1 — sezony 2021–2025 | xG per mecz, forecast |
| **football-data.co.uk** | 12 lig × 5 sezonów (2425–2021) | strzały, rożne, kartki, kursy |
| **Flashscore archiwum piłki** | World Cup 2026/2022/2018, Euro 2024/2020 | wyniki + statystyki meczu |
| **Flashscore archiwum tenisa** | 8 Grand Slamów (ATP+WTA) + crawl turniejów ATP/WTA | wyniki + statystyki (serwis, return itd.) |

Ligi football-data poza top-5: Szkocja, Holandia, Belgia, Portugalia, Turcja, Grecja (+ Championship).

Opcja `crawl_tennis_tournaments` (domyślnie `true`) przeszukuje strony turniejów ATP/WTA — może trwać kilka minut; wyłącz w configu jeśli potrzebujesz tylko Grand Slamów.

Import archiwum Flashscore pobiera statystyki meczu dla pierwszych 300 rekordów (`archive_stats_limit`); pełny backfill statystyk dla starszych meczów można powtórzyć z wyższym limitem.

## Uwagi

- SofaScore API może zwracać `403` — pipeline działa dalej z Flashscore + Understat.
- Pełne kursy bukmacherskie z OddsPortal wymagają odszyfrowania feedów; obecnie zapisywane są metadane, payload i modelowe kursy.
- Understat daje xG i forecast dla wspieranych lig (EPL, La Liga, Serie A, Bundesliga, Ligue 1).
- W przerwie sezonowej piłkarskiej domyślne okno 45 dni obejmuje start lig (EPL, La Liga itd.) oraz bieżące kwalifikacje UEFA.
- Tenis: ATP/WTA/Challenger + Grand Slamy z aktywnego menu Flashscore; ITF i deble są domyślnie odfiltrowane.
- Archiwa Flashscore (WC, Euro, Wimbledon) korzystają z feedu `results` na stronach `draw/` — pełny drabinkowy turniej (np. ~140 meczów Wimbledon ATP). Starsze edycje bez osobnej strony mogą być niekompletne; pełniejsza historia piłki pochodzi z Understat i football-data.
