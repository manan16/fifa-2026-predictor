CREATE TABLE IF NOT EXISTS teams (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    fifa_code TEXT,
    confederation TEXT,
    fifa_ranking INTEGER,
    elo_rating INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS fixtures (
    id SERIAL PRIMARY KEY,
    match_number INTEGER UNIQUE,
    stage TEXT,
    group_name TEXT,
    home_team_id INTEGER REFERENCES teams(id),
    away_team_id INTEGER REFERENCES teams(id),
    venue TEXT,
    city TEXT,
    kickoff_time TIMESTAMP,
    status TEXT,
    home_score INTEGER,
    away_score INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS team_match_stats (
    id SERIAL PRIMARY KEY,
    team_id INTEGER REFERENCES teams(id),
    fixture_id INTEGER REFERENCES fixtures(id),
    goals_for INTEGER,
    goals_against INTEGER,
    shots INTEGER,
    shots_on_target INTEGER,
    corners INTEGER,
    corners_conceded INTEGER,
    possession NUMERIC,
    yellow_cards INTEGER,
    red_cards INTEGER,
    xg NUMERIC,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    fixture_id INTEGER REFERENCES fixtures(id),
    model_version TEXT,
    home_win_probability NUMERIC,
    draw_probability NUMERIC,
    away_win_probability NUMERIC,
    predicted_home_goals INTEGER,
    predicted_away_goals INTEGER,
    confidence TEXT,
    explanation_json JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS historical_matches (
    id SERIAL PRIMARY KEY,
    date DATE,
    home_team TEXT,
    away_team TEXT,
    home_score INTEGER,
    away_score INTEGER,
    tournament TEXT,
    neutral BOOLEAN,
    country TEXT
);

