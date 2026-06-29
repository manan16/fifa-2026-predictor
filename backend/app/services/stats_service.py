"""Wikipedia-sourced match statistics pipeline.

Wikipedia content is licensed CC BY-SA, so reuse is fine *with attribution*.
We pull World Cup 2026 match data from the stable MediaWiki ``action=parse``
API (NOT by scraping rendered CSS, which is brittle) and parse the
``{{Football box}}`` templates that the encyclopedia reliably carries: the
score, the goalscorer lists, and cards where present. Possession, shots,
shots on target, corners and xG are usually absent on Wikipedia football boxes
and are left ``NULL`` rather than fabricated.

The pipeline is deliberately defensive: any single page or match that fails to
fetch/parse is logged and skipped, never fatal to the whole run.
"""

from __future__ import annotations

import re
from typing import Any

import requests

from app.db.connection import get_connection, get_dict_cursor

# Wikipedia requires a descriptive User-Agent that identifies the application.
USER_AGENT = (
    "FIFA2026Predictor/1.0 (https://github.com/fifa-2026-predictor; "
    "match-stats sync) requests/python"
)
WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"

# A small, fixed set of tournament pages that carry the {{Football box}}
# structures for the 2026 knockout matches. Kept short so we are polite to
# Wikipedia (few calls per run).
WIKIPEDIA_PAGES = (
    "2026 FIFA World Cup knockout stage",
)

# Map Wikipedia's team names onto the names seeded in our ``teams`` table.
# Keys are normalized (lower-cased, whitespace-collapsed); values are the exact
# seeded display names.
_TEAM_NAME_ALIASES = {
    "united states": "USA",
    "usa": "USA",
    "u.s.a.": "USA",
    "us": "USA",
    "dr congo": "Congo DR",
    "congo dr": "Congo DR",
    "democratic republic of the congo": "Congo DR",
    "democratic republic of congo": "Congo DR",
    "dr. congo": "Congo DR",
    "bosnia and herzegovina": "Bosnia-Herz",
    "bosnia-herzegovina": "Bosnia-Herz",
    "bosnia and herz.": "Bosnia-Herz",
    "bosnia-herz": "Bosnia-Herz",
    "ivory coast": "Ivory Coast",
    "côte d'ivoire": "Ivory Coast",
    "cote d'ivoire": "Ivory Coast",
    "côte d’ivoire": "Ivory Coast",
}

# team_match_stats columns we write (id/created_at are managed by the table).
_STATS_COLUMNS = (
    "team_id",
    "fixture_id",
    "goals_for",
    "goals_against",
    "shots",
    "shots_on_target",
    "corners",
    "corners_conceded",
    "possession",
    "yellow_cards",
    "red_cards",
    "xg",
)

# Metrics Wikipedia football boxes don't reliably carry. Left NULL, never faked.
_ABSENT_METRICS = {
    "shots": None,
    "shots_on_target": None,
    "corners": None,
    "corners_conceded": None,
    "possession": None,
    "xg": None,
}

_SCORE_RE = re.compile(r"(\d+)\s*[–\-]\s*(\d+)")
_YELLOW_CARD_RE = re.compile(r"\{\{\s*(?:yel|yellow card|yellow-card)\b", re.IGNORECASE)
_RED_CARD_RE = re.compile(
    r"\{\{\s*(?:sent off|red card|red-card|yellow-red card|second yellow|rc)\b",
    re.IGNORECASE,
)


def _clean(value: str | None) -> str:
    """Strip wiki/flag markup from a raw template value down to plain text."""
    if not value:
        return ""
    text = value.strip()
    # Drop {{flagicon|...}} / {{fb|XXX}} style flag templates entirely.
    text = re.sub(r"\{\{\s*(?:flagicon|fb|fbicon|flagathlete)[^{}]*\}\}", "", text, flags=re.IGNORECASE)
    # Reduce [[Target|Label]] -> Label and [[Target]] -> Target.
    text = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]+)\]\]", r"\1", text)
    # Drop any remaining templates and stray markup.
    text = re.sub(r"\{\{[^{}]*\}\}", "", text)
    text = text.replace("'''", "").replace("''", "")
    return re.sub(r"\s+", " ", text).strip()


def normalize_team_name(name: str | None) -> str:
    """Resolve a Wikipedia team name to the seeded team name.

    Unknown names are returned cleaned but otherwise untouched so ordinary teams
    (e.g. "Brazil") still match. The tricky World Cup names — "DR Congo",
    "Bosnia and Herzegovina", "United States", "Côte d'Ivoire" — collapse onto
    the exact seeded spellings.
    """
    cleaned = _clean(name)
    key = cleaned.lower().strip()
    return _TEAM_NAME_ALIASES.get(key, cleaned)


def _parse_template_params(body: str) -> dict[str, str]:
    """Split a template body into ``key -> value`` pairs.

    Splits on top-level ``|`` only, respecting nested ``{{ }}`` and ``[[ ]]`` so
    goalscorer templates like ``{{goal|45}}`` don't break the parse. The text
    before the first top-level ``|`` is the template name and is discarded.
    """
    parts: list[str] = []
    depth_brace = 0
    depth_bracket = 0
    current: list[str] = []
    i = 0
    while i < len(body):
        pair = body[i : i + 2]
        if pair == "{{":
            depth_brace += 1
            current.append(pair)
            i += 2
            continue
        if pair == "}}":
            depth_brace = max(0, depth_brace - 1)
            current.append(pair)
            i += 2
            continue
        if pair == "[[":
            depth_bracket += 1
            current.append(pair)
            i += 2
            continue
        if pair == "]]":
            depth_bracket = max(0, depth_bracket - 1)
            current.append(pair)
            i += 2
            continue
        char = body[i]
        if char == "|" and depth_brace == 0 and depth_bracket == 0:
            parts.append("".join(current))
            current = []
            i += 1
            continue
        current.append(char)
        i += 1
    parts.append("".join(current))

    params: dict[str, str] = {}
    for segment in parts[1:]:  # parts[0] is the template name
        if "=" not in segment:
            continue
        key, _, value = segment.partition("=")
        params[key.strip().lower()] = value.strip()
    return params


def extract_football_boxes(wikitext: str) -> list[dict[str, str]]:
    """Find every ``{{Football box...}}`` template and return its params."""
    boxes: list[dict[str, str]] = []
    lowered = wikitext.lower()
    search_from = 0
    while True:
        start = lowered.find("{{football box", search_from)
        if start == -1:
            break
        # Walk forward to the matching closing braces.
        depth = 0
        i = start
        end = -1
        while i < len(wikitext) - 1:
            pair = wikitext[i : i + 2]
            if pair == "{{":
                depth += 1
                i += 2
                continue
            if pair == "}}":
                depth -= 1
                i += 2
                if depth == 0:
                    end = i
                    break
                continue
            i += 1
        if end == -1:
            break
        body = wikitext[start + 2 : end - 2]
        boxes.append(_parse_template_params(body))
        search_from = end
    return boxes


def _parse_score(score: str | None) -> tuple[int | None, int | None]:
    if not score:
        return (None, None)
    match = _SCORE_RE.search(_clean(score))
    if not match:
        return (None, None)
    return (int(match.group(1)), int(match.group(2)))


def _count_cards(text: str | None) -> tuple[int, int]:
    if not text:
        return (0, 0)
    return (len(_YELLOW_CARD_RE.findall(text)), len(_RED_CARD_RE.findall(text)))


def parse_football_box(params: dict[str, str]) -> dict[str, Any] | None:
    """Turn a parsed ``{{Football box}}`` params dict into a match record.

    Returns ``None`` when the box lacks the two team names — there is nothing we
    can match against in that case.
    """
    team1 = normalize_team_name(params.get("team1"))
    team2 = normalize_team_name(params.get("team2"))
    if not team1 or not team2:
        return None

    home_score, away_score = _parse_score(params.get("score"))
    home_yellow, home_red = _count_cards(params.get("goals1"))
    away_yellow, away_red = _count_cards(params.get("goals2"))

    return {
        "team1": team1,
        "team2": team2,
        "team1_goals_for": home_score,
        "team1_goals_against": away_score,
        "team2_goals_for": away_score,
        "team2_goals_against": home_score,
        "team1_yellow_cards": home_yellow,
        "team1_red_cards": home_red,
        "team2_yellow_cards": away_yellow,
        "team2_red_cards": away_red,
    }


def _fetch_wikitext(page_title: str) -> str:
    """Fetch raw wikitext for a page via the MediaWiki ``parse`` API."""
    response = requests.get(
        WIKIPEDIA_API,
        params={
            "action": "parse",
            "page": page_title,
            "prop": "wikitext",
            "format": "json",
            "formatversion": "2",
            "redirects": "1",
        },
        headers={"User-Agent": USER_AGENT},
        timeout=20,
    )
    response.raise_for_status()
    return response.json()["parse"]["wikitext"]


def fetch_match_stats(pages: tuple[str, ...] = WIKIPEDIA_PAGES) -> list[dict[str, Any]]:
    """Fetch and parse Football box match records from Wikipedia.

    Per-page and per-box failures are logged and skipped so a single broken
    match never aborts the run.
    """
    matches: list[dict[str, Any]] = []
    for page in pages:
        try:
            wikitext = _fetch_wikitext(page)
        except Exception as exc:  # pragma: no cover - network/HTTP failure path
            print(f"Wikipedia stats: failed to fetch '{page}': {exc}")
            continue
        for box in extract_football_boxes(wikitext):
            try:
                parsed = parse_football_box(box)
            except Exception as exc:
                print(f"Wikipedia stats: failed to parse a football box on '{page}': {exc}")
                continue
            if parsed:
                matches.append(parsed)
    return matches


def _load_fixtures() -> list[dict[str, Any]]:
    with get_dict_cursor() as cur:
        cur.execute(
            """
            SELECT
                f.id,
                f.home_team_id,
                f.away_team_id,
                ht.name AS home_team_name,
                at.name AS away_team_name
            FROM fixtures f
            JOIN teams ht ON f.home_team_id = ht.id
            JOIN teams at ON f.away_team_id = at.id;
            """
        )
        return list(cur.fetchall())


def match_to_fixture(match: dict[str, Any], fixtures: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Find the seeded fixture for a parsed match by normalized team names."""
    team1 = match["team1"].lower()
    team2 = match["team2"].lower()
    for fixture in fixtures:
        home = normalize_team_name(fixture.get("home_team_name")).lower()
        away = normalize_team_name(fixture.get("away_team_name")).lower()
        if {team1, team2} == {home, away}:
            return fixture
    return None


def build_team_stats(match: dict[str, Any], fixture: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Project a parsed match onto home/away ``team_match_stats`` rows.

    Orients ``team1``/``team2`` from Wikipedia onto the fixture's home/away
    sides, regardless of which order Wikipedia listed them.
    """
    home_name = normalize_team_name(fixture.get("home_team_name")).lower()
    if match["team1"].lower() == home_name:
        home_prefix, away_prefix = "team1", "team2"
    else:
        home_prefix, away_prefix = "team2", "team1"

    def row(prefix: str, team_id: int) -> dict[str, Any]:
        return {
            "team_id": team_id,
            "goals_for": match[f"{prefix}_goals_for"],
            "goals_against": match[f"{prefix}_goals_against"],
            "yellow_cards": match[f"{prefix}_yellow_cards"],
            "red_cards": match[f"{prefix}_red_cards"],
            **_ABSENT_METRICS,
        }

    home_stats = row(home_prefix, fixture["home_team_id"])
    away_stats = row(away_prefix, fixture["away_team_id"])
    return home_stats, away_stats


def upsert_team_match_stats(
    fixture_id: int,
    home_stats: dict[str, Any],
    away_stats: dict[str, Any],
) -> None:
    """Write the home and away rows for a fixture idempotently.

    ``team_match_stats`` has no unique constraint on (team_id, fixture_id), so we
    make writes idempotent by deleting any existing rows for the fixture before
    inserting the fresh pair. Running this twice yields exactly one pair of rows.
    """
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM team_match_stats WHERE fixture_id = %s;", (fixture_id,))
        for stats in (home_stats, away_stats):
            values = {**stats, "fixture_id": fixture_id}
            columns = ", ".join(_STATS_COLUMNS)
            placeholders = ", ".join(["%s"] * len(_STATS_COLUMNS))
            cur.execute(
                f"INSERT INTO team_match_stats ({columns}) VALUES ({placeholders});",
                tuple(values.get(column) for column in _STATS_COLUMNS),
            )
    conn.commit()


def sync_wikipedia_match_stats() -> int:
    """Fetch Wikipedia match stats and upsert them onto matching fixtures.

    Returns the number of fixtures updated. Any single match that fails to match
    or persist is logged and skipped, never fatal to the run.
    """
    fixtures = _load_fixtures()
    if not fixtures:
        return 0

    records = 0
    for match in fetch_match_stats():
        try:
            fixture = match_to_fixture(match, fixtures)
            if fixture is None:
                continue
            home_stats, away_stats = build_team_stats(match, fixture)
            upsert_team_match_stats(fixture["id"], home_stats, away_stats)
            records += 1
        except Exception as exc:
            print(
                f"Wikipedia stats: skipping {match.get('team1')} vs {match.get('team2')}: {exc}"
            )
    return records
