import aiohttp
from datetime import date, timedelta
from config import BIGBALLS_API_KEY, TOP_LEAGUES
import random

HEADERS = {
    "Authorization": f"Bearer {BIGBALLS_API_KEY}"
}

BASE_URL = "https://api.bigballsdata.com/v1"


async def get_leagues_list():
    return list(TOP_LEAGUES.items())


async def get_fixtures_by_league(league_key: str, days: int = 5):
    """
    Get fixtures for a league using Big Balls Sports Data
    """
    fixtures = []
    url = f"{BASE_URL}/matches"
    params = {
        "sport": "football",
        "league": league_key,
        "status": "scheduled"  # or "all"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=HEADERS, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    matches = data.get("data", []) or data.get("matches", []) or data

                    for item in matches[:15]:  # limit to 15
                        home = item.get("home", {}).get("name") or item.get("home_team") or "Home"
                        away = item.get("away", {}).get("name") or item.get("away_team") or "Away"
                        match_date = item.get("date") or item.get("kickoff") or item.get("start_time") or "TBD"
                        match_id = item.get("id") or item.get("match_id") or random.randint(10000, 99999)

                        fixtures.append({
                            "id": match_id,
                            "date": str(match_date)[:16],
                            "status": item.get("status", "NS"),
                            "home": home,
                            "away": away,
                            "league": TOP_LEAGUES.get(league_key, league_key),
                            "league_id": league_key,
                        })
                else:
                    print(f"Big Balls API Error: {resp.status}")
    except Exception as e:
        print(f"Error fetching from Big Balls: {e}")

    # Fallback mock data if API returns nothing
    if not fixtures:
        fixtures = get_mock_fixtures(league_key)

    return fixtures


def get_mock_fixtures(league_key: str):
    league_name = TOP_LEAGUES.get(league_key, "League")
    mock_teams = {
        "epl": [("Arsenal", "Chelsea"), ("Liverpool", "Man City"), ("Tottenham", "Newcastle")],
        "laliga": [("Real Madrid", "Barcelona"), ("Atletico Madrid", "Sevilla")],
        "seriea": [("Inter", "Juventus"), ("Milan", "Napoli")],
        "bundesliga": [("Bayern Munich", "Dortmund"), ("Leverkusen", "Leipzig")],
        "ligue1": [("PSG", "Marseille"), ("Lyon", "Monaco")],
    }

    teams = mock_teams.get(league_key, [("Home Team", "Away Team"), ("Team A", "Team B")])
    fixtures = []

    for i, (home, away) in enumerate(teams):
        fixtures.append({
            "id": 800000 + i,
            "date": (date.today() + timedelta(days=i)).strftime("%Y-%m-%d 18:00"),
            "status": "NS",
            "home": home,
            "away": away,
            "league": league_name,
            "league_id": league_key,
        })
    return fixtures
