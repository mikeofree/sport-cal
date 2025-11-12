from flask import Flask, Response
import requests
from datetime import datetime, timedelta, timezone
from icalendar import Calendar, Event
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Simple in-memory cache
CACHE = {
    "nfl": {"last_fetch": None, "ical_bytes": None},
    "nba": {"last_fetch": None, "ical_bytes": None},
}

REFRESH_INTERVAL = timedelta(hours=24)


def iso_to_utc(dt_str: str) -> datetime:
    """
    Convert ESPN ISO8601 date string to timezone-aware UTC datetime.
    Example: '2025-11-12T18:20Z' or '2025-11-12T18:20:00Z'
    """
    if dt_str.endswith("Z"):
        dt_str = dt_str.replace("Z", "+00:00")
    dt = datetime.fromisoformat(dt_str)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def build_calendar(events, prodid: str, uid_prefix: str, default_hours: int) -> bytes:
    """
    Build an ICS calendar from ESPN events.
    """
    cal = Calendar()
    cal.add("prodid", prodid)
    cal.add("version", "2.0")

    # Include games from a reasonable window:
    # - 30 days in the past
    # - 365 days into the future
    today = datetime.now(timezone.utc).date()
    start_window = today - timedelta(days=30)
    end_window = today + timedelta(days=365)

    for ev in events.values():
        try:
            start = iso_to_utc(ev["date"])
        except Exception as e:
            logging.warning(f"Failed to parse date for event {ev.get('id')}: {e}")
            continue

        if not (start_window <= start.date() <= end_window):
            continue

        comp = ev.get("competitions", [])[0]
        teams = comp.get("competitors", [])

        home = next((t for t in teams if t.get("homeAway") == "home"), None)
        away = next((t for t in teams if t.get("homeAway") == "away"), None)

        if not home or not away:
            continue

        home_name = home["team"]["displayName"]
        away_name = away["team"]["displayName"]

        summary = f"{away_name} @ {home_name}"
        uid = f"{uid_prefix}-{ev['id']}@sports"

        end = start + timedelta(hours=default_hours)

        event = Event()
        event.add("summary", summary)
        event.add("dtstart", start)
        event.add("dtend", end)
        event.add("uid", uid)

        # Optional: location and status
        venue = comp.get("venue", {}).get("fullName")
        if venue:
            event.add("location", venue)

        status = ev.get("status", {}).get("type", {}).get("description")
        if status:
            event.add("description", status)

        cal.add_component(event)

    return cal.to_ical()


def fetch_league_events(league: str):
    """
    Fetch and combine all events for a league by looping over team schedules.
    league = 'nfl' or 'nba'
    """
    if league == "nfl":
        sport_path = "football"
        default_hours = 3  # approx game length
        prodid = "-//Homepage Sports Calendar//NFL//EN"
        uid_prefix = "nfl"
    elif league == "nba":
        sport_path = "basketball"
        default_hours = 2.5
        prodid = "-//Homepage Sports Calendar//NBA//EN"
        uid_prefix = "nba"
    else:
        raise ValueError("Unsupported league")

    base_team_url = f"https://site.api.espn.com/apis/site/v2/sports/{sport_path}/{league}/teams"
    logging.info(f"Fetching {league.upper()} team list from ESPN: {base_team_url}")
    resp = requests.get(base_team_url, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    teams = data["sports"][0]["leagues"][0]["teams"]
    logging.info(f"Found {len(teams)} {league.upper()} teams")

    events_by_id = {}

    for t in teams:
        team_info = t.get("team") or {}
        team_id = team_info.get("id")
        if not team_id:
            continue

        sched_url = f"https://site.api.espn.com/apis/site/v2/sports/{sport_path}/{league}/teams/{team_id}/schedule"
        logging.info(f"Fetching schedule for {league.upper()} team {team_info.get('displayName')} (ID {team_id})")
        try:
            s_resp = requests.get(sched_url, timeout=10)
            s_resp.raise_for_status()
            s_data = s_resp.json()
        except Exception as e:
            logging.warning(f"Failed to fetch schedule for team {team_id}: {e}")
            continue

        for ev in s_data.get("events", []):
            ev_id = ev.get("id")
            if not ev_id:
                continue
            # Deduplicate: same game appears in both teams' schedules
            events_by_id[ev_id] = ev

    logging.info(f"Total unique {league.upper()} events: {len(events_by_id)}")

    ical_bytes = build_calendar(
        events_by_id,
        prodid=prodid,
        uid_prefix=uid_prefix,
        default_hours=default_hours,
    )

    return ical_bytes


def get_cached_calendar(league: str):
    """
    Return cached ICS bytes for league, refreshing if older than REFRESH_INTERVAL.
    """
    now = datetime.now(timezone.utc)
    league_cache = CACHE[league]

    if league_cache["last_fetch"] is None or league_cache["ical_bytes"] is None:
        logging.info(f"No cache for {league.upper()}, fetching initial data...")
    elif now - league_cache["last_fetch"] > REFRESH_INTERVAL:
        logging.info(f"Cache for {league.upper()} is stale, refreshing...")
    else:
        # Cache is fresh
        return league_cache["ical_bytes"]

    try:
        ical_bytes = fetch_league_events(league)
        league_cache["ical_bytes"] = ical_bytes
        league_cache["last_fetch"] = now
        logging.info(f"Updated {league.upper()} calendar cache at {now.isoformat()}")
        return ical_bytes
    except Exception as e:
        logging.error(f"Error refreshing {league.upper()} schedule: {e}")
        # Fallback: if we had a previous cache, serve it
        if league_cache["ical_bytes"] is not None:
            logging.info(f"Serving stale {league.upper()} calendar due to error")
            return league_cache["ical_bytes"]
        # Otherwise, propagate error
        raise


@app.route("/nfl.ics")
def nfl_ics():
    ical_bytes = get_cached_calendar("nfl")
    return Response(ical_bytes, mimetype="text/calendar")


@app.route("/nba.ics")
def nba_ics():
    ical_bytes = get_cached_calendar("nba")
    return Response(ical_bytes, mimetype="text/calendar")


@app.route("/")
def root():
    return (
        "Sports ICS server is running. Available feeds: /nfl.ics, /nba.ics\n",
        200,
        {"Content-Type": "text/plain"},
    )


if __name__ == "__main__":
    # Dev server; for production, put behind a real WSGI server (gunicorn, etc.)
    app.run(host="0.0.0.0", port=5000)
