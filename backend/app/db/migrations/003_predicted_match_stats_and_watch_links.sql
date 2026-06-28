CREATE TABLE IF NOT EXISTS predicted_match_stats (
    id SERIAL PRIMARY KEY,
    fixture_id INTEGER NOT NULL REFERENCES fixtures(id),
    model_version TEXT,
    expected_home_goals NUMERIC,
    expected_away_goals NUMERIC,
    home_shots INTEGER,
    away_shots INTEGER,
    home_shots_on_target INTEGER,
    away_shots_on_target INTEGER,
    home_possession NUMERIC,
    away_possession NUMERIC,
    home_corners INTEGER,
    away_corners INTEGER,
    home_yellow_cards INTEGER,
    away_yellow_cards INTEGER,
    home_red_card_probability NUMERIC,
    away_red_card_probability NUMERIC,
    both_teams_to_score_probability NUMERIC,
    over_2_5_goals_probability NUMERIC,
    clean_sheet_home_probability NUMERIC,
    clean_sheet_away_probability NUMERIC,
    explanation_json JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE predicted_match_stats
    ADD COLUMN IF NOT EXISTS explanation_json JSONB;

CREATE INDEX IF NOT EXISTS idx_predicted_match_stats_fixture_created
    ON predicted_match_stats (fixture_id, created_at DESC);

CREATE TABLE IF NOT EXISTS actual_match_stats (
    id SERIAL PRIMARY KEY,
    fixture_id INTEGER NOT NULL REFERENCES fixtures(id),
    home_shots INTEGER,
    away_shots INTEGER,
    home_shots_on_target INTEGER,
    away_shots_on_target INTEGER,
    home_possession NUMERIC,
    away_possession NUMERIC,
    home_corners INTEGER,
    away_corners INTEGER,
    home_yellow_cards INTEGER,
    away_yellow_cards INTEGER,
    home_red_cards INTEGER,
    away_red_cards INTEGER,
    source TEXT,
    last_sync TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_actual_match_stats_fixture_created
    ON actual_match_stats (fixture_id, created_at DESC);

CREATE TABLE IF NOT EXISTS watch_links (
    id SERIAL PRIMARY KEY,
    fixture_id INTEGER NOT NULL REFERENCES fixtures(id),
    region TEXT,
    provider_name TEXT,
    provider_type TEXT,
    url TEXT,
    is_official BOOLEAN DEFAULT false,
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (fixture_id, region, provider_name)
);

CREATE INDEX IF NOT EXISTS idx_watch_links_fixture
    ON watch_links (fixture_id);
