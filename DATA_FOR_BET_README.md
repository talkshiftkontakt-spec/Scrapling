# Data for Bet

Sports data API and scraping pipeline for **football** and **tennis** — upcoming fixtures, prematch stats, odds snapshots, and played match history.

Built on [Scrapling](https://github.com/talkshiftkontakt-spec/Scrapling) fetchers + Flashscore / Understat / football-data.co.uk.

## Quick start

```bash
pip install -e ".[sportsdata]"
cp .env.example .env

# import data (first run takes a while)
sportsdata run-all

# start API
sportsdata serve --port 8080
```

Open:
- API docs: http://localhost:8080/docs
- Dashboard: http://localhost:8080/dashboard/
- Health: http://localhost:8080/health

## Docker

```bash
docker compose -f docker-compose.yml up --build
```

## API endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | pipeline health |
| GET | `/summary` | counts + DB stats |
| GET | `/upcoming` | upcoming events + prematch stats + odds |
| GET | `/events/{id}` | single upcoming event |
| GET | `/results` | played matches (paginated) |
| GET | `/results/{id}` | single played match |
| POST | `/jobs/{name}` | run sync job |

### Query params

**`/upcoming` and `/results`**
- `sport=football|tennis`
- `league=Wimbledon`
- `participant=Sinner`
- `from_date=2025-01-01`
- `to_date=2025-12-31`
- `limit=50`
- `offset=0`

**`/results` only**
- `source=flashscore|understat|football-data.co.uk`
- `has_stats=true|false`

### Pagination response

```json
{
  "items": [...],
  "total": 10161,
  "limit": 50,
  "offset": 0,
  "has_more": true
}
```

## Connect from your app

### TypeScript

```ts
import { SportsDataClient } from "./client/sportsdata-client";

const client = new SportsDataClient(
  process.env.SPORTSDATA_API_URL ?? "http://localhost:8080",
  process.env.SPORTSDATA_API_KEY,
);

const tennis = await client.listResults({
  sport: "tennis",
  league: "Wimbledon",
  limit: 100,
});

console.log(tennis.total, tennis.items.length);
```

### Next.js env

```env
SPORTSDATA_API_URL=http://localhost:8080
SPORTSDATA_API_KEY=optional-if-enabled
```

### curl

```bash
curl "http://localhost:8080/results?sport=tennis&limit=5"
curl -H "X-API-Key: your-key" http://localhost:8080/summary
```

## Jobs

```bash
sportsdata fixtures          # upcoming matches
sportsdata stats             # prematch enrich
sportsdata odds              # odds snapshots
sportsdata results           # recent finished matches
sportsdata history           # full historical import
sportsdata stats-backfill --sport tennis
sportsdata run-all
```

## Data coverage

| Source | Content |
|---|---|
| Flashscore | upcoming + played matches, match stats |
| Understat | xG (top 5 leagues, 2021–2025) |
| football-data.co.uk | 12 leagues × 5 seasons, shots/cards/odds |
| Archives | World Cup, Euro, ATP/WTA/Challenger Grand Slams |

## Security (optional)

```env
SPORTSDATA_API_KEY=your-secret
SPORTSDATA_REQUIRE_API_KEY=true
SPORTSDATA_CORS_ORIGINS=http://localhost:3000
```

Send header: `X-API-Key: your-secret`

## License

Private project — see LICENSE.
