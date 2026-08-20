import aiohttp
from datetime import date
from config import API_FOOTBALL_KEY, TOP_LEAGUES

async def get_todays_fixtures():
    if not API_FOOTBALL_KEY:
        return _mock_fixtures()
    
    today = date.today().isoformat()
    fixtures = []
    
    async with aiohttp.ClientSession() as session:
        for league_id, league_name in TOP_LEAGUES.items():
            url = f"https://v3.football.api-sports.io/fixtures?league={league_id}&season=2025&date={today}"
            headers = {"x-apisports-key": API_FOOTBALL_KEY}
            try:
                async with session.get(url, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        for item in data.get("response", []):
                            fixtures.append({
                                "id": item["fixture"]["id"],
                                "league": league_name,
                                "home": item["teams"]["home"]["name"],
                                "away": item["teams"]["away"]["name"],
                                "time": item["fixture"]["date"][11:16],
                                "status": item["fixture"]["status"]["short"],
                            })
            except Exception:
                continue
    return fixtures if fixtures else _mock_fixtures()

def _mock_fixtures():
    return [
        {"id": 1, "league": "Premier League", "home": "Arsenal", "away": "Chelsea", "time": "19:00", "status": "NS"},
        {"id": 2, "league": "La Liga", "home": "Real Madrid", "away": "Barcelona", "time": "20:00", "status": "NS"},
        {"id": 3, "league": "Serie A", "home": "Inter", "away": "Juventus", "time": "18:45", "status": "NS"},
        {"id": 4, "league": "Bundesliga", "home": "Bayern Munich", "away": "Dortmund", "time": "17:30", "status": "NS"},
        {"id": 5, "league": "Ligue 1", "home": "PSG", "away": "Marseille", "time": "20:45", "status": "NS"},
                              ]
