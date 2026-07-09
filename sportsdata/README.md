# SportsData Pipeline

Implementacja planu z `docs/sports-data-scraping-plan.md`.

## Co robi system

- **Faza 0**: synchronizacja przyszłych meczów piłki i tenisu z Flashscore
- **Faza 1**: statystyki przedmeczowe (forma, H2H, xG z Understat, best-effort SofaScore)
- **Faza 2**: snapshoty kursów z OddsPortal + modelowe kursy z Understat
- **Faza 3**: API, dashboard, monitoring jobów, backfill historyczny z football-data.co.uk

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

# eksport JSON
sportsdata export --output data/upcoming.json

# API + dashboard
sportsdata serve --port 8080
```

## Endpointy API

- `GET /health`
- `GET /upcoming?sport=football|tennis`
- `GET /events/{id}`
- `POST /jobs/{fixtures_sync|stats_enrich|odds_snapshot|pre_match_boost|backfill|all}`
- `GET /dashboard/`

## Baza danych

Domyślnie SQLite: `data/sportsdata.db`

Tabele:
- `events`
- `event_stats_prematch`
- `odds_snapshots`
- `job_runs`
- `historical_matches`

## Uwagi

- SofaScore API może zwracać `403` — pipeline działa dalej z Flashscore + Understat.
- Pełne kursy bukmacherskie z OddsPortal wymagają odszyfrowania feedów; obecnie zapisywane są metadane, payload i modelowe kursy.
- Understat daje xG i forecast dla wspieranych lig (EPL, La Liga, Serie A, Bundesliga, Ligue 1).
- W przerwie sezonowej piłkarskiej domyślne okno 45 dni obejmuje start lig (EPL, La Liga itd.) oraz bieżące kwalifikacje UEFA.
- Tenis: ATP/WTA/Challenger + Grand Slamy z aktywnego menu Flashscore; ITF i deble są domyślnie odfiltrowane.
