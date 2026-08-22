import aiohttp
from datetime import date, datetime, timedelta
from config import API_FOOTBALL_KEY, TOP_LEAGUES

HEADERS = {
    "x-apisports-key": API_FOOTBALL_KEY
}

async def get_leagues_list():
    """Return list of top leagues as (id, name)"""
    return list(TOP_LEAGUES.items())


async def get_fixtures_by_league(league_id: int, days: int = 3):
    """
    Get fixtures for a league for today + next few days.
    Returns list of matches.
    """
    fixtures = []
    today = date.today()

    async with aiohttp.ClientSession() as session:
        for i in range(days):
            check_date = (today + timedelta(days=i)).isoformat()
            url = f"https://v3.football.api-sports.io/fixtures?league={league_id}&season=2025&date={check_date}"

            try:
                async with session.get(url, headers=HEADERS) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        for item in data.get("response", []):
                            fixture = item.get("fixture", {})
                            teams = item.get("teams", {})
                            league = item.get("league", {})

                            fixtures.append({
                                "id": fixture.get("id"),
                                "date": fixture.get("date", "")[:16].replace("T", " "),
                                "status": fixture.get("status", {}).get("short", "NS"),
                                "home": teams.get("home", {}).get("name", "Home"),
                                "away": teams.get("away", {}).get("name", "Away"),
                                "league": league.get("name", "Unknown"),
                                "league_id": league_id,
                            })
            except Exception as e:
                print(f"Error fetching fixtures: {e}")
                continue

    return fixtures


async def get_fixture_details(fixture_id: int):
    """Get more details for a specific match (optional)"""
    url = f"https://v3.football.api-sports.io/fixtures?id={fixture_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=HEADERS) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("response", [])
    return []
