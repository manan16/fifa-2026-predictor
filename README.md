# FIFA 2026 Knockout Predictor

![Screenshot placeholder](docs/screenshot-placeholder.svg)

Portfolio-quality MVP for predicting FIFA World Cup 2026 knockout-stage outcomes with a Flask API, PostgreSQL, raw SQL migrations, psycopg 3, and a React analytics dashboard.

## Tech Stack

- Backend: Python 3.10+, Flask, Flask-CORS, psycopg 3, pandas, scikit-learn, pytest
- Database: PostgreSQL, raw SQL migrations, no SQLAlchemy, no Alembic
- Frontend: React, Vite, TypeScript, Tailwind CSS, Recharts
- Infrastructure: Docker, docker-compose, Makefile, `.env.example`

## Features

- Team and fixture APIs backed by PostgreSQL
- Raw SQL migration runner with `schema_migrations`
- Idempotent seed script with 32 knockout teams and 31 demo bracket fixtures
- Elo-inspired baseline model with Poisson-style scoreline projection
- 90-minute win/draw/loss probabilities
- Knockout advance probabilities for non-group matches
- Responsive React dashboard with fixture detail, teams table, and model notes
- Backend pytest coverage for routes and model probabilities

## Repository Structure

```text
fifa-2026-predictor/
  backend/
    app/
      db/
      ml/
      routes/
    tests/
  frontend/
    src/
      components/
      pages/
      services/
      types/
  data/
  notebooks/
  docker-compose.yml
  Makefile
```

## Local Setup Without Docker

Create a `.env` from the example and make sure PostgreSQL is running locally.

```bash
cp .env.example .env
make install
make migrate
make seed
make backend
```

In another terminal:

```bash
make frontend
```

Open `http://localhost:5173`. The backend runs at `http://localhost:9000`.

## Local Setup With Docker

```bash
cp .env.example .env
make docker-up
```

Docker starts PostgreSQL, runs migrations and seed data, then serves:

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:9000`
- PostgreSQL: `localhost:5432`

Stop containers with:

```bash
make docker-down
```

## Database

Run migrations:

```bash
cd backend && python -m app.db.migrate
```

Seed demo knockout bracket data:

```bash
cd backend && python -m app.db.seed
```

Tables include `teams`, `fixtures`, `team_match_stats`, `predictions`, `historical_matches`, and `schema_migrations`.

## API Endpoints

```text
GET  /health
GET  /api/teams
GET  /api/teams/<team_id>
GET  /api/fixtures
GET  /api/fixtures/<fixture_id>
GET  /api/predictions
GET  /api/predictions/<fixture_id>
POST /api/predict
```

Example custom prediction:

```bash
curl -X POST http://localhost:9000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"home_team":"Brazil","away_team":"Japan","neutral_venue":true,"stage":"Round of 32"}'
```

## Prediction Model

The MVP model is intentionally transparent:

1. Calculate a team strength score from Elo rating and FIFA ranking.
2. Apply optional home advantage only when `neutral_venue` is false.
3. Convert strength difference into expected goals.
4. Use a compact Poisson score matrix to estimate home win, draw, and away win probabilities.
5. Pick a rounded predicted scoreline and confidence label.
6. For knockout stages, split draw probability into advance probabilities.

This is a baseline, not a certainty engine. It is designed to be replaced later by a trained model once historical match ingestion and evaluation are available.

## Testing

```bash
make test
```

The initial tests cover health, teams, fixtures, prediction routes, probability sums, and confidence labels.

## Roadmap

- Visual bracket simulator page
- Live API-Football integration
- Official FIFA fixture ingestion
- Historical international match ingestion
- Betting odds baseline
- Player injuries and suspensions
- xG-based features
- Corners, cards, possession, and shots features
- Monte Carlo tournament simulation
- Bracket predictor
- Model evaluation using Brier score and log loss
- Prediction history tracking
- Admin panel for refreshing fixtures
- Scheduled jobs for updating results
- Model retraining pipeline

## Known Limitations

- Knockout fixtures are demo data based on the reference bracket image, not an official FIFA feed.
- Kickoff times are stored as London-local demo timestamps.
- Seeded team ratings are realistic but illustrative.
- No live official FIFA feed is connected yet.
- The model does not account for injuries, squad selection, travel, rest, weather, or tactical style.
- Frontend authentication and admin tooling are intentionally out of scope for the MVP.
