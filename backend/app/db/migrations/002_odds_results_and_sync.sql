ALTER TABLE fixtures
    ADD COLUMN IF NOT EXISTS actual_home_score INTEGER,
    ADD COLUMN IF NOT EXISTS actual_away_score INTEGER,
    ADD COLUMN IF NOT EXISTS home_penalties INTEGER,
    ADD COLUMN IF NOT EXISTS away_penalties INTEGER,
    ADD COLUMN IF NOT EXISTS winner_team_id INTEGER REFERENCES teams(id),
    ADD COLUMN IF NOT EXISTS external_event_id TEXT,
    ADD COLUMN IF NOT EXISTS result_source TEXT,
    ADD COLUMN IF NOT EXISTS last_result_sync TIMESTAMP,
    ADD COLUMN IF NOT EXISTS last_odds_sync TIMESTAMP;

CREATE TABLE IF NOT EXISTS bookmakers (
    id SERIAL PRIMARY KEY,
    key TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    region TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS fixture_odds (
    id SERIAL PRIMARY KEY,
    fixture_id INTEGER REFERENCES fixtures(id),
    bookmaker_id INTEGER REFERENCES bookmakers(id),
    source TEXT NOT NULL,
    market_key TEXT NOT NULL,
    outcome_name TEXT NOT NULL,
    outcome_type TEXT NOT NULL,
    decimal_price NUMERIC,
    implied_probability NUMERIC,
    normalized_probability NUMERIC,
    last_update TIMESTAMP,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_fixture_odds_fixture_market
    ON fixture_odds (fixture_id, market_key);

CREATE TABLE IF NOT EXISTS odds_consensus (
    id SERIAL PRIMARY KEY,
    fixture_id INTEGER REFERENCES fixtures(id),
    market_key TEXT NOT NULL,
    home_probability NUMERIC,
    draw_probability NUMERIC,
    away_probability NUMERIC,
    bookmaker_count INTEGER,
    average_home_odds NUMERIC,
    average_draw_odds NUMERIC,
    average_away_odds NUMERIC,
    best_home_odds NUMERIC,
    best_draw_odds NUMERIC,
    best_away_odds NUMERIC,
    source TEXT,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_odds_consensus_fixture_market
    ON odds_consensus (fixture_id, market_key, calculated_at DESC);

CREATE TABLE IF NOT EXISTS sync_runs (
    id SERIAL PRIMARY KEY,
    job_name TEXT NOT NULL,
    status TEXT NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP,
    message TEXT,
    records_processed INTEGER DEFAULT 0
);
