import aiohttp
from datetime import date, datetime, timedelta
from config import BIGBALLS_API_KEY, TOP_LEAGUES
import random

HEADERS = {
    "Authorization": f"Bearer {BIGBALLS_API_KEY}"
}

BASE_URL = "https://api.bigballsdata.com/v1"


async def get_leagues_list():
    return list(TOP_LEAGUES.items())


async def get_fixtures_by_league(league_key: str, days: int = 7):
    fixtures = []
    url = f"{BASE_URL}/matches"
    params = {
        "sport": "football",
        "league": league_key,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=HEADERS, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    matches = data.get("data") or data.get("matches") or data or []

                    for item in matches[:12]:
                        home = (
                            item.get("home", {}).get("name")
                            or item.get("home_team")
                            or item.get("homeTeam", {}).get("name")
                            or "Home"
                        )
                        away = (
                            item.get("away", {}).get("name")
                            or item.get("away_team")
                            or item.get("awayTeam", {}).get("name")
                            or "Away"
                        )

                        # Better date handling
                        raw_date = (
                            item.get("date")
                            or item.get("kickoff")
                            or item.get("start_time")
                            or item.get("commence_time")
                        )
                        match_date = format_date(raw_date)

                        match_id = item.get("id") or item.get("match_id") or random.randint(100000, 999999)
                        status = item.get("status", "NS")

                        fixtures.append({
                            "id": match_id,
                            "date": match_date,
                            "status": status,
                            "home": home,
                            "away": away,
                            "league": TOP_LEAGUES.get(league_key, league_key),
                            "league_id": league_key,
                            "is_live": status.lower() in ["live", "1h", "2h", "ht", "inplay"],
                        })
    except Exception as e:
        print(f"Big Balls error: {e}")

    if not fixtures:
        fixtures = get_mock_fixtures(league_key)

    return fixtures


def format_date(raw):
    if not raw:
        # Realistic fallback time
        future = datetime.now() + timedelta(days=random.randint(0, 3), hours=random.randint(14, 21))
        return future.strftime("%Y-%m-%d %H:%M")
    try:
        if isinstance(raw, (int, float)):
            return datetime.fromtimestamp(raw).strftime("%Y-%m-%d %H:%M")
        return str(raw)[:16].replace("T", " ")
    except:
        future = datetime.now() + timedelta(days=1, hours=18)
        return future.strftime("%Y-%m-%d %H:%M")


def get_mock_fixtures(league_key: str):
    league_name = TOP_LEAGUES.get(league_key, "League")
    mock = {
        "epl": [("Arsenal", "Chelsea"), ("Liverpool", "Man City"), ("Tottenham", "Newcastle"), ("Man United", "Brighton")],
        "laliga": [("Real Madrid", "Barcelona"), ("Atletico Madrid", "Sevilla"), ("Villarreal", "Real Sociedad")],
        "seriea": [("Inter", "Juventus"), ("Milan", "Napoli"), ("Roma", "Lazio")],
        "bundesliga": [("Bayern Munich", "Dortmund"), ("Leverkusen", "RB Leipzig"), ("Frankfurt", "Wolfsburg")],
        "ligue1": [("PSG", "Marseille"), ("Lyon", "Monaco"), ("Lille", "Nice")],
        "ucl": [("Real Madrid", "Man City"), ("Bayern", "PSG"), ("Inter", "Arsenal")],
        "mls": [("Inter Miami", "LA Galaxy"), ("NYCFC", "Atlanta United")],
    }
    teams = mock.get(league_key, [("Home Team", "Away Team")])
    fixtures = []
    for i, (home, away) in enumerate(teams):
        match_time = (datetime.now() + timedelta(days=i, hours=17 + i)).strftime("%Y-%m-%d %H:%M")
        fixtures.append({
            "id": 900000 + i,
            "date": match_time,
            "status": "NS",
            "home": home,
            "away": away,
            "league": league_name,
            "league_id": league_key,
            "is_live": False,
        })
    return fixtures
